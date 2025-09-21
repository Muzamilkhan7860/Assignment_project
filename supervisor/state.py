from typing import TypedDict, Optional, List, Dict

class GraphState(TypedDict):
    objective: Optional[str]
    todos: Optional[List[str]]
    completed: Optional[List[str]]
    artifacts: Optional[Dict[str, str]]
    summaries: Optional[List[str]]
    python_script: Optional[str]
    subagent_logs: Optional[List[str]]
