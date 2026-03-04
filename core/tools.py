import os
import subprocess
from typing import Optional

class ToolExecutor:
    def __init__(self, workspace_path: str):
        self.workspace_path = os.path.expanduser(workspace_path)
        if not os.path.exists(self.workspace_path):
            os.makedirs(self.workspace_path)

    def _full_path(self, path: str) -> str:
        # Prevent path traversal
        normalized = os.path.normpath(os.path.join(self.workspace_path, path))
        if not normalized.startswith(self.workspace_path):
            raise ValueError("Path is outside the workspace")
        return normalized

    def create_file(self, path: str, content: str) -> str:
        try:
            full_path = self._full_path(path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"File created successfully at {path}"
        except Exception as e:
            return f"Error creating file: {str(e)}"

    def edit_file(self, path: str, old: str, new: str) -> str:
        try:
            full_path = self._full_path(path)
            if not os.path.exists(full_path):
                return f"Error: File {path} does not exist"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old not in content:
                return f"Error: Could not find exact match for text to replace in {path}"
            
            new_content = content.replace(old, new, 1) # Replace first occurrence
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return f"File {path} edited successfully"
        except Exception as e:
            return f"Error editing file: {str(e)}"

    def read_file(self, path: str) -> str:
        try:
            full_path = self._full_path(path)
            if not os.path.exists(full_path):
                return f"Error: File {path} does not exist"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def run_command(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\nError Output:\n{result.stderr}"
            return output if output else "Command executed successfully (no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except Exception as e:
            return f"Error running command: {str(e)}"
