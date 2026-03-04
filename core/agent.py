import json
import re
from typing import Generator, List, Dict, Any
from .ollama_client import OllamaClient
from .tools import ToolExecutor

SYSTEM_PROMPT = """You are a powerful AI coding agent. You follow the ReAct pattern (Reasoning -> Action -> Observation).

Your goal is to help the user with their coding tasks. You can interact with the file system and run commands.

SIEMPRE responde en formato JSON con los campos: "thought", "action", "params".

Available actions:
1. create_file: {"path": "file_path", "content": "file_content"}
2. edit_file: {"path": "file_path", "old": "text_to_replace", "new": "replacement_text"}
3. read_file: {"path": "file_path"}
4. run_command: {"command": "shell_command"}
5. finish: {"content": "final_response_to_user"}

Example of a response:
{
  "thought": "I need to check the contents of main.py to understand the structure.",
  "action": "read_file",
  "params": {"path": "main.py"}
}

Wait for the "observation" after each action. Use "finish" when you have completed the task.
Limit your reasoning to 10 steps max.
"""

class Agent:
    def __init__(self, workspace_path: str, model: str = "qwen2.5-coder:7b"):
        self.ollama = OllamaClient(model)
        self.tools = ToolExecutor(workspace_path)
        self.history: List[Dict[str, str]] = []
        self.max_steps = 10

    def run(self, user_input: str) -> Generator[Dict[str, Any], None, None]:
        self.history.append({"role": "user", "content": user_input})
        
        for step in range(self.max_steps):
            full_response = ""
            # Stream the agent's thought/action from Ollama
            for chunk in self.ollama.chat_stream(self.history, system=SYSTEM_PROMPT):
                full_response += chunk
            
            # Clean response if it contains markdown code blocks
            clean_json = self._extract_json(full_response)
            
            try:
                data = json.loads(clean_json)
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
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        # Or just use the whole text if it looks like JSON
        return text.strip()

    def _execute_tool(self, action: str, params: Dict[str, Any]) -> str:
        if action == "create_file":
            return self.tools.create_file(params.get("path"), params.get("content", ""))
        elif action == "edit_file":
            return self.tools.edit_file(params.get("path"), params.get("old", ""), params.get("new", ""))
        elif action == "read_file":
            return self.tools.read_file(params.get("path"))
        elif action == "run_command":
            return self.tools.run_command(params.get("command"))
        else:
            return f"Unknown action: {action}"
