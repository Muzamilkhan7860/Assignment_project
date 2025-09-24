import os, json
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langsmith import Client
from supervisor.state import GraphState
from supervisor.subagent import run_subagent
from supervisor.llm_client import call_deepseek
from supervisor.utils import sanitize_filename, persist_artifact_to_disk
from supervisor.vfs import VirtualFileSystem

vfs = VirtualFileSystem()
langsmith_client = Client()

ARTIFACTS_DIR = os.getenv("PROJECT_ARTIFACT_DIR", "./artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def update_todo(state: GraphState, task_done: str, new_tasks=None):
    state.setdefault("todos", [])
    state.setdefault("completed", [])
    if task_done in state["todos"]:
        state["todos"].remove(task_done)
        state["completed"].append(task_done)
    if new_tasks:
        state["todos"].extend(new_tasks)
    return state


def supervisor_node(state: GraphState):
    if not state.get("todos"):
        obj = state.get("objective", "")
        state["todos"] = [
            f"Search for information about: {obj}",
            "Summarize top findings",
            "Write a Python script based on the objective",
        ]
        state["completed"], state["subagent_logs"], state["artifacts"], state["summaries"] = [], [], {}, []

    while state["todos"]:
        task = state["todos"][0]
        sub = run_subagent(
            task,
            ["read_file", "write_file", "edit_file", "execute_code", "search_internet", "web_scrape"],
        )

        try:
            state["subagent_logs"].append(json.dumps(sub, indent=2, default=str))
        except Exception:
            state["subagent_logs"].append(str(sub))

        for name, path in sub.get("artifacts", {}).items():
            state["artifacts"][name] = path

        if "Search for information" in task:
            for r in sub.get("results", []):
                if isinstance(r, dict) and "search_internet" in r:
                    for item in r["search_internet"]:
                        title = item.get("title", "")
                        snippet = item.get("snippet", "")
                        if title or snippet:
                            state["summaries"].append(f"{title} — {snippet}")

        if "Summarize top findings" in task:
            raw = state.get("summaries", [])
            if not raw:
                raw = ["No results found."]
            messages = [
                {"role": "system", "content": "You are a helpful summarization assistant."},
                {"role": "user", "content": f"Summarize these findings clearly:\n{raw}"},
            ]
            try:
                clean_summary = call_deepseek(messages)
            except Exception:
                clean_summary = "No summarization available (LLM call failed)."
            state["summaries"] = [clean_summary]

            fname = sanitize_filename("clean_summary") + ".txt"
            persist_artifact_to_disk(fname, clean_summary)
            vfs.write_file(fname, clean_summary)
            state["artifacts"][fname] = os.path.join(ARTIFACTS_DIR, fname)

        if "Write a Python script" in task:
            messages = [
                {"role": "system", "content": "You are a Python coding assistant. ONLY output runnable Python code."},
                {"role": "user", "content": f"Write a runnable Python script that completes this objective:\n\n{state.get('objective', '')}\n\nEnsure it is executable as-is."},
            ]
            try:
                script = call_deepseek(messages)
            except Exception:
                script = "# LLM failed to produce script\n"

            if script.strip().startswith("```"):
                script = script.strip().lstrip("```").rstrip("```")
                if script.startswith("python\n"):
                    script = script.replace("python\n", "", 1)

            script_fname = "generated_script.py"
            vfs.write_file(script_fname, script)
            persist_artifact_to_disk(script_fname, script)
            state["python_script"] = script
            state["artifacts"][script_fname] = os.path.join(ARTIFACTS_DIR, script_fname)

        update_todo(state, task)

    return state


workflow = StateGraph(GraphState)
workflow.add_node("supervisor", supervisor_node)
workflow.set_entry_point("supervisor")
# graph = workflow.compile(checkpointer=MemorySaver())   #for  running main.py file

graph = workflow.compile()


def run_supervisor(objective: str):
    state = {"objective": objective}

    final_state = graph.invoke(
        state,
        config={
            "configurable": {"thread_id": "demo-thread"},
            "langsmith": {
                "project_name": "SupervisorDemo",
                "client": langsmith_client,
            },
        },
    )

    out = os.path.join(ARTIFACTS_DIR, "final_output.txt")

    with open(out, "w") as f:
        f.write(json.dumps(final_state, indent=2, default=str))

    print(f"Results saved to {out}")
    return final_state
