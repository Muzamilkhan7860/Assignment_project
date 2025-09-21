import os
import uuid

ARTIFACTS_DIR = os.getenv("PROJECT_ARTIFACT_DIR", "./artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def sanitize_filename(text: str, max_length: int = 40) -> str:
    safe = text[:max_length].replace(" ", "_").replace(":", "").replace("/", "_").replace("\\", "_")
    return f"{safe}_{uuid.uuid4().hex[:8]}"

def persist_artifact_to_disk(filename: str, content: str) -> str:
    path = os.path.join(ARTIFACTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def is_code_task(task_text: str) -> bool:
    return any(kw in task_text.lower() for kw in ["python", "code", "script", "execute", ".py", "function", "implement"])
