import json
import os
from typing import Dict, List, Any, Optional

DEFAULT_CONFIG = {
    "ollama_url": "http://localhost:11434",
    "brave_api_key": "",
    "agents": [
        {
            "id": "default",
            "name": "Orchestrator 🦕",
            "prompt": "You are a powerful AI coding agent. You follow the ReAct pattern (Reasoning -> Action -> Observation).\n\nIMPORTANT: You must output YOUR ENTIRE RESPONSE as a valid JSON object with the following keys:\n- \"thought\": Your internal reasoning.\n- \"action\": The tool to use (one of the below).\n- \"params\": A dictionary of arguments for the tool.\n\nTOOLS:\n- get_system_info: Get current date, time, OS and workspace info.\n- search_files(pattern): Search for files in the workspace using a glob pattern (e.g. '*.py').\n- read_file(path): Read content of a file.\n- create_file(path, content): Create a new file.\n- edit_file(path, old, new): Edit an existing file by replacing 'old' text with 'new' text.\n- run_command(command): Run a terminal command.\n- search_web(query): Search the internet for information if you don't know the answer or need latest docs.\n- finish(content): Finish the task and provide a final response.\n\nAlways use get_system_info if you need temporal awareness. NEVER say you will do something without providing an 'action'.",
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
        "search_web": True
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
                # Merge with default to ensure all keys exist
                for key, val in DEFAULT_CONFIG.items():
                    if key not in data:
                        data[key] = val
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
