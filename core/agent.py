import json
import re
import os
from typing import Generator, List, Dict, Any, Optional
from .ollama_client import OllamaClient
from .tools import ToolExecutor
from .config import ConfigManager

class Agent:
    def __init__(self, workspace_manager, model: Optional[str] = None):
        self.config_manager = ConfigManager()
        self.ollama = OllamaClient(model)
        self.workspace_manager = workspace_manager
        self.tools = ToolExecutor(workspace_manager.get_root())
        self.history: List[Dict[str, str]] = []
        self.max_steps = 10
        
        # Load active agent configuration
        agent_conf = self.config_manager.get_active_agent()
        self.system_prompt = agent_conf.get("prompt", "")
        self.name = agent_conf.get("name", "Agent")

    def run(self, user_input: str) -> Generator[Dict[str, Any], None, None]:
        # Sync workspace path
        root = self.workspace_manager.get_root()
        if root:
            self.tools.workspace_path = os.path.abspath(os.path.expanduser(root))
        
        self.history.append({"role": "user", "content": user_input})
        
        # Inject dynamic context snapshot
        context = self.workspace_manager.get_context_snapshot()
        dynamic_system_prompt = self.system_prompt + "\n---\n" + context

        # Yield initial thinking state
        yield {"type": "thought", "content": "Consultando a Ollama..."}
        
        for step in range(self.max_steps):
            full_response = ""
            # Stream the agent's thought/action from Ollama
            for chunk in self.ollama.chat_stream(self.history, system=dynamic_system_prompt):
                full_response += chunk
            
            # Clean and repair JSON
            clean_json = self._extract_json(full_response)
            
            try:
                data = json.loads(clean_json, strict=False)
                thought = data.get("thought", "Thinking...")
                action = data.get("action")
                params = data.get("params", {})
                
                yield {"type": "thought", "content": thought}
                
                if not action or action == "finish":
                    yield {"type": "final", "content": params.get("content", full_response)}
                    self.history.append({"role": "assistant", "content": full_response})
                    return

                yield {"type": "action", "action": action, "params": params}
                
                # Execute tool
                observation = self._execute_tool(action, params)
                yield {"type": "observation", "content": observation}
                
                # Add step to history
                self.history.append({"role": "assistant", "content": full_response})
                self.history.append({"role": "user", "content": f"Observation: {observation}"})
                
            except Exception as e:
                yield {"type": "error", "content": f"Failed to parse agent response: {str(e)}\nRaw: {full_response}"}
                return

        yield {"type": "error", "content": "Maximum reasoning steps reached."}

    def _extract_json(self, text: str) -> str:
        # Try to find JSON inside markdown blocks
        json_str = text
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Fallback: look for the first { and last }
            start = text.find('{')
            end = text.rfind('}')
            if start != -1:
                if end != -1 and end > start:
                    json_str = text[start:end+1]
                else:
                    json_str = text[start:]
        
        # Repair common JSON errors from LLMs
        # 1. Remove trailing commas before } or ]
        json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
        
        # 2. Structural repair for truncated JSON (balance braces/brackets)
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
            
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        if open_brackets > close_brackets:
            json_str += ']' * (open_brackets - close_brackets)
            
        return json_str.strip()

    def _execute_tool(self, action: str, params: Dict[str, Any]) -> str:
        if action == "create_file":
            return self.tools.create_file(params.get("path"), params.get("content", ""))
        elif action == "edit_file":
            return self.tools.edit_file(params.get("path"), params.get("old", ""), params.get("new", ""))
        elif action == "read_file":
            return self.tools.read_file(params.get("path"))
        elif action == "list_files":
            return self._list_files_tool(params.get("pattern", "*"))
        else:
            return f"Unknown action: {action}"

    def _list_files_tool(self, pattern: str) -> str:
        if not self.tools.workspace_path:
            return "Error: No workspace opened. Please open a folder first."
        import fnmatch
        files = []
        for root, _, filenames in os.walk(self.tools.workspace_path):
            for filename in fnmatch.filter(filenames, pattern):
                files.append(os.path.relpath(os.path.join(root, filename), self.tools.workspace_path))
        return "\n".join(files) if files else "No files found matching the pattern."
