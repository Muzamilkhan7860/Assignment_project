import os
from typing import Dict, Any

class VirtualFileSystem:
    def __init__(self):
        self.files: Dict[str, str] = {}

    def read_file(self, path: str) -> str:
        return self.files.get(path, "")

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        self.files[path] = content
        return {"path": path, "bytes_written": len(content)}

    def edit_file(self, path: str, edits: Any) -> Dict[str, Any]:
        content = self.files.get(path, "")
        if isinstance(edits, list):
            for edit in edits:
                content = content.replace(edit["find"], edit["replace"])
        else:
            content = edits
        self.files[path] = content
        return {"path": path, "content": content}
