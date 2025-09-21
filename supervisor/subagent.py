import json, time
from typing import Dict, Any, List
from supervisor.utils import sanitize_filename, persist_artifact_to_disk, is_code_task
from supervisor.vfs import VirtualFileSystem
from supervisor.llm_client import call_deepseek
from tools_registry import TOOLS_REGISTRY

vfs = VirtualFileSystem()

def build_subagent_prompt(task: str, available_tools: List[str]) -> str:
    return f"""
You are a Subagent. Complete this task with a structured plan.

Task: {task}

Allowed tools: {', '.join(available_tools)}

Output JSON:
{{
  "tools": [],
  "notes": "short notes",
  "results": {{}},
  "code": "optional Python code"
}}
"""

def run_subagent(task: str, tools: List[str], max_retries: int = 2) -> Dict[str, Any]:
    prompt_text = build_subagent_prompt(task, tools)
    messages = [{"role": "system", "content": "You output JSON plans."},
                {"role": "user", "content": prompt_text}]

    # Parse LLM plan
    try:
        plan_text = call_deepseek(messages)
        first, last = plan_text.find("{"), plan_text.rfind("}")
        json_snip = plan_text[first:last+1] if first != -1 and last != -1 else plan_text
        plan = json.loads(json_snip)
    except Exception:
        plan, plan_text = {"tools": tools, "notes": "fallback plan", "code": None}, "{}"

    results, artifacts = [], {}

    def save_artifact(base_name, content):
        fname = sanitize_filename(base_name) + ".txt"
        vfs.write_file(fname, content)
        path = persist_artifact_to_disk(fname, content)
        artifacts[fname] = path
        return path

    # Inline results
    inline = plan.get("results")
    if inline and isinstance(inline, dict):
        save_artifact("inline_results", json.dumps(inline, indent=2))
        results.append({"inline_results": inline})

    # Code execution
    code = plan.get("code")
    if code and "execute_code" in tools:
        exec_func = TOOLS_REGISTRY.get("execute_code")
        if callable(exec_func):
            try:
                out = exec_func(code)
                results.append({"execute_code": out})
                save_artifact("subagent_code", code)
            except Exception as e:
                results.append({"execute_code_error": str(e)})

    # Other tools
    for tool in tools:
        if tool == "write_file":
            content = f"Artifact for task: {task}\nnotes: {plan.get('notes','')}"
            fname = sanitize_filename(f"{task}_write") + ".txt"
            vfs.write_file(fname, content)
            artifacts[fname] = persist_artifact_to_disk(fname, content)
            results.append({"write_file": fname})
        elif tool == "read_file":
            results.append({"read_file": vfs.read_file(sanitize_filename(f"{task}_read") + ".txt")})
        elif tool == "search_internet":
            func = TOOLS_REGISTRY.get("search_internet")
            if func:
                resp = func(task)
                save_artifact(f"{task}_search", json.dumps(resp, indent=2))
                results.append({"search_internet": resp})

    if not artifacts:
        save_artifact(f"{task}_none", f"No artifacts for {task}")

    return {"prompt": prompt_text, "plan_text": plan_text, "plan": plan,
            "task": task, "tools_used": tools, "results": results, "artifacts": artifacts}
