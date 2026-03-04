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
            "prompt": "You are a powerful AI coding agent capable of interacting with the real world. You follow the ReAct pattern (Thought -> Action -> Observation).\n\nCRITICAL RULES:\n1. ALWAYS output your response as a SINGLE JSON OBJECT.\n2. NEVER output plain text outside the JSON.\n3. If you need information you don't have, ALWAYS use search_web or search_files first. DO NOT apologize or say you cannot do it.\n4. Do not use 'finish' until you have actually accomplished the goal.\n\nJSON FORMAT:\n{\n  \"thought\": \"I need to find X...\",\n  \"action\": \"tool_name\",\n  \"params\": {\"arg\": \"val\"}\n}\n\nEXAMPLE TOOL USAGE:\nRequest: 'Who is Okan iD?'\nResponse:\n{\n  \"thought\": \"I don't have information about 'Okan iD' in my knowledge. I need to search the web.\",\n  \"action\": \"search_web\",\n  \"params\": {\"query\": \"Okan iD\"}\n}\n\nTOOLS:\n- get_system_info: Current date/time/OS/workspace.\n- search_files(pattern): Glob search (e.g. '*.py').\n- read_file(path): Read file content.\n- create_file(path, content): New file.\n- edit_file(path, old, new): Edit file.\n- run_command(command): Terminal command.\n- search_web(query): Search the internet using Brave Search API.\n- finish(content): Provide final answer to user.\n\nYou ARE connected to the internet via search_web. Use it.",
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
