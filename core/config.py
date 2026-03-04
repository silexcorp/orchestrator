import json
import os
from typing import Dict, List, Any, Optional

DEFAULT_CONFIG = {
    "ollama_url": "http://localhost:11434",
    "brave_api_key": "",
    "gemini_api_key": "",
    "remote_model": "gemini-2.0-flash",
    "preferred_provider": "ollama",
    "agents": [
        {
            "id": "default",
            "name": "Orchestrator 🦕",
            "prompt": "You are a Senior Software Engineer AI Agent. Your goal is to solve complex coding tasks within this project autonomously and reliably.\n\nOPERATING MODE: ReAct (Thought -> Action -> Observation).\n\nHOW TO WORK:\n1. EXPLORE: When asked for a change, first use 'search_files' and 'grep_search' to find all relevant code. Don't assume you know where everything is.\n2. READ: Use 'read_file' to understand the code before suggesting any edits.\n3. PLAN: Internalize the project's architecture and coding style.\n4. EXECUTE: Use 'edit_file' or 'create_file' to implement the solution. \n5. VERIFY: ALWAYS use 'run_command' to run tests, linters, or try to build the project after your changes. If you break something, fix it immediately.\n6. COMPLETE: Only use 'finish' when you have verified that the task is fully accomplished and functional.\n\nCRITICAL RULES:\n- ALWAYS output a single JSON object.\n- NEVER use placeholders. Provide complete, functional code.\n- Be concise but thorough.\n- If a file is long, read it in chunks if necessary (your current 'read_file' supports full reading, but be selective).\n\nJSON FORMAT:\n{\n  \"thought\": \"Detailed reasoning about the project state and next steps...\",\n  \"action\": \"tool_name\",\n  \"params\": {\"arg\": \"val\"}\n}\n\nTOOLS:\n- get_system_info: System context (OS, date, workspace).\n- search_files(pattern): Find files by name glob.\n- grep_search(query): Find string occurrences across all files.\n- read_file(path): Read complete content of a file.\n- create_file(path, content): Create a new file with full content.\n- edit_file(path, old, new): Replace 'old' text block with 'new' text block exactly.\n- run_command(command): Execute any shell command in the workspace.\n- search_web(query): Search the internet for documentation or solutions.\n- finish(content): Final message to the user with a summary of accomplishment.\n",
            "color": "#00f2ff"
        },
        {
            "id": "creative",
            "name": "Creative Assistant",
            "prompt": "You are a creative coding assistant. You focus on beautiful UI, animations, and clean architectures. Use get_system_info for context and search_web for inspiration.",
            "color": "#8a2be2"
        }
    ],
    "tools": {
        "create_file": True,
        "edit_file": True,
        "run_command": True,
        "list_files": True,
        "read_file": True,
        "get_system_info": True,
        "search_files": True,
        "search_web": True,
        "grep_search": True
    },
    "active_agent_id": "default"
}

class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.orchestrator_ai")
        self.config_file = os.path.join(self.config_dir, "config.json")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        self.config = self.load()

    def load(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_file):
            self.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Merge top-level keys
                for key, val in DEFAULT_CONFIG.items():
                    if key not in data:
                        data[key] = val
                
                # Deep merge tools
                if "tools" in data:
                    for tool_id, enabled in DEFAULT_CONFIG["tools"].items():
                        if tool_id not in data["tools"]:
                            data["tools"][tool_id] = enabled

                # HEURISTIC: Force update "default" prompt if it's old or lacks tools info
                for agent in data.get("agents", []):
                    if agent.get("id") == "default":
                        current_prompt = agent.get("prompt", "")
                        # If it's the very old placeholder prompt, update it to latest.
                        if "Your goal is to help the user with their coding tasks" in current_prompt or "search_web" not in current_prompt:
                            agent["prompt"] = DEFAULT_CONFIG["agents"][0]["prompt"]
                            print("Updated default agent prompt to latest version.")

                self.config = data
                return data
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG

    def save(self, data: Dict[str, Any] = None):
        if data:
            self.config = data
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_agents(self) -> List[Dict[str, Any]]:
        return self.config.get("agents", [])

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        for agent in self.get_agents():
            if agent["id"] == agent_id:
                return agent
        return None

    def get_active_agent(self) -> Dict[str, Any]:
        active_id = self.config.get("active_agent_id", "default")
        return self.get_agent(active_id) or self.get_agents()[0]

    def set_active_agent(self, agent_id: str):
        self.config["active_agent_id"] = agent_id
        self.save()
