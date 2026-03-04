import json
import os
from typing import Dict, List, Any, Optional

DEFAULT_CONFIG = {
    "ollama_url": "http://localhost:11434",
    "agents": [
        {
            "id": "default",
            "name": "Orchestrator 🦕",
            "prompt": "You are a powerful AI coding agent. You follow the ReAct pattern (Reasoning -> Action -> Observation). Your goal is to help the user with their coding tasks. You can interact with the file system and run commands.",
            "color": "#00f2ff"
        },
        {
            "id": "creative",
            "name": "Creative Assistant",
            "prompt": "You are a creative coding assistant. You focus on beautiful UI, animations, and clean architectures.",
            "color": "#8a2be2"
        }
    ],
    "tools": {
        "create_file": True,
        "edit_file": True,
        "run_command": True,
        "list_files": True,
        "read_file": True
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
