import os
import subprocess
import datetime
import platform
import fnmatch
from typing import Optional, List

class ToolExecutor:
    def __init__(self, workspace_path: Optional[str]):
        self.workspace_path = os.path.abspath(os.path.expanduser(workspace_path)) if workspace_path else None
        if self.workspace_path and not os.path.exists(self.workspace_path):
            os.makedirs(self.workspace_path)

    def _full_path(self, path: str) -> str:
        if not self.workspace_path:
            raise ValueError("No workspace opened. Please open a folder first.")
        # Prevent path traversal
        normalized = os.path.normpath(os.path.join(self.workspace_path, path))
        if not normalized.startswith(self.workspace_path):
            raise ValueError("Path is outside the workspace")
        return normalized

    def get_system_info(self) -> str:
        """Returns current date, time, day of the week, and OS info."""
        now = datetime.datetime.now()
        info = [
            f"Current Date: {now.strftime('%Y-%m-%d')}",
            f"Current Time: {now.strftime('%H:%M:%S')}",
            f"Day of the Week: {now.strftime('%A')}",
            f"Operating System: {platform.system()} {platform.release()}",
            f"Working Directory: {self.workspace_path or os.getcwd()}"
        ]
        return "\n".join(info)

    def search_files(self, pattern: str) -> str:
        """Search for files matching a glob pattern in the workspace."""
        if not self.workspace_path:
            return "Error: No workspace opened."
        
        matches = []
        for root, _, filenames in os.walk(self.workspace_path):
            for filename in fnmatch.filter(filenames, pattern):
                rel_path = os.path.relpath(os.path.join(root, filename), self.workspace_path)
                matches.append(rel_path)
        
        if not matches:
            return f"No files found matching pattern: {pattern}"
        return "\n".join(matches)

    def search_web(self, query: str, api_key: str) -> str:
        """Search the web using Brave Search API."""
        if not api_key:
            return "Error: Brave Search API Key not configured. Please add it in Settings -> Search."
        
        try:
            import httpx
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
            params = {"q": query, "count": 5}
            
            response = httpx.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("web", {}).get("results", []):
                title = item.get("title")
                url = item.get("url")
                snippet = item.get("description")
                results.append(f"Title: {title}\nSnippet: {snippet}\nURL: {url}\n")
            
            if not results:
                return "No web results found."
            return "\n---\n".join(results)
            
        except Exception as e:
            return f"Error performing web search: {str(e)}"

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
            
            # Robust matching: try exact match first
            if old in content:
                new_content = content.replace(old, new, 1)
            else:
                # Try matching without leading/trailing whitespace in 'old'
                stripped_old = old.strip()
                if stripped_old and stripped_old in content:
                    # Find the actual chunk including its surrounding whitespace
                    # This is a bit complex, but let's try a simpler approach for now:
                    # If stripped version matches exactly once, we can use it.
                    occurrences = content.count(stripped_old)
                    if occurrences == 1:
                        new_content = content.replace(stripped_old, new, 1)
                    else:
                        return f"Error: Could not find exact match for text to replace in {path}. " \
                               f"Multiple similar matches found ({occurrences}), be more specific."
                else:
                    return f"Error: Could not find exact match for text to replace in {path}. " \
                           f"Make sure you copied the block EXACTLY as it appears in the file."
            
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

    def grep_search(self, query: str) -> str:
        """Search for a string across all files in the workspace (ignoring common junk folders)."""
        if not self.workspace_path:
            return "Error: No workspace opened."
        
        ignored_dirs = {'.git', 'venv', '.venv', '__pycache__', 'node_modules', 'dist', 'build'}
        results = []
        
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                # Efficiently skip ignored directories
                dirs[:] = [d for d in dirs if d not in ignored_dirs]
                
                for filename in files:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, self.workspace_path)
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                if query in line:
                                    results.append(f"{rel_path}:{line_num}: {line.strip()}")
                                    if len(results) > 100:
                                        return "\n".join(results) + "\n... (Too many results, showing first 100)"
                    except Exception:
                        continue # Skip binary or unreadable files
                        
            if not results:
                return f"No occurrences of '{query}' found in workspace."
            return "\n".join(results)
            
        except Exception as e:
            return f"Error during grep search: {str(e)}"

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
