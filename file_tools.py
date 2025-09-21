import difflib

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path: str, content: str) -> dict:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"path": path, "bytes_written": len(content)}

def edit_file(path: str, edits) -> dict:
    old_content = read_file(path)
    if isinstance(edits, str):  # whole-file replace
        new_content = edits
    else:  # list of find/replace
        new_content = old_content
        for e in edits:
            new_content = new_content.replace(e["find"], e["replace"])

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    diff = "\n".join(difflib.unified_diff(old_content.splitlines(), new_content.splitlines()))
    return {"path": path, "diff": diff}
