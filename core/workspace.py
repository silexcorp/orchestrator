import os
from typing import List, Optional

class WorkspaceManager:
    def __init__(self):
        self.root_path: Optional[str] = None
        self.active_file_path: Optional[str] = None
        self.active_file_content: str = ""

    def open_folder(self, path: str):
        self.root_path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)

    def get_root(self) -> Optional[str]:
        return self.root_path

    def set_active_file(self, path: str, content: str):
        self.active_file_path = path
        self.active_file_content = content

    def list_files(self, extensions: List[str] = None) -> List[str]:
        if not self.root_path:
            return []
        
        ignored_dirs = {'__pycache__', '.git', 'node_modules', '.venv', 'venv'}
        valid_extensions = set(extensions) if extensions else {'.py', '.md', '.txt', '.json', '.toml', '.env', '.yaml'}
        
        files_list = []
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                if any(file.endswith(ext) for ext in valid_extensions):
                    rel_path = os.path.relpath(os.path.join(root, file), self.root_path)
                    files_list.append(rel_path)
        
        return files_list

    def get_context_snapshot(self) -> str:
        if not self.root_path:
            return "No workspace opened."
        
        snapshot = f"WORKSPACE: {self.root_path}\n\n"
        snapshot += "ESTRUCTURA DE ARCHIVOS:\n"
        
        files = self.list_files()
        if len(files) > 50:
            # Simple list for large projects
            for f in files[:50]:
                snapshot += f"  {f}\n"
            snapshot += f"... and {len(files) - 50} more files.\n"
        else:
            # Build a simple tree-like string
            for f in files:
                snapshot += f"  {f}\n"
        
        snapshot += f"\nARCHIVO ACTIVO EN EL EDITOR: {self.active_file_path or 'Ninguno'}\n"
        if self.active_file_path:
            snapshot += "\nCONTENIDO DEL ARCHIVO ACTIVO:\n"
            snapshot += "```python\n"
            # Limit content to first 300 lines for the active file
            lines = self.active_file_content.splitlines()[:300]
            snapshot += "\n".join(lines) + ("\n..." if len(self.active_file_content.splitlines()) > 300 else "")
            snapshot += "\n```\n"
        
        # Add relevant small files (context)
        snapshot += "\nARCHIVOS RELEVANTES:\n"
        relevant_files = [f for f in files if f != self.active_file_path][:3]
        for rf in relevant_files:
            full_path = os.path.join(self.root_path, rf)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read().splitlines()[:100] # Limit to 100 lines
                    snapshot += f"--- {rf} ---\n"
                    snapshot += "\n".join(content) + "\n"
            except:
                continue

        return snapshot
