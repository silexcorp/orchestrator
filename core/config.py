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
            "prompt": "You are a Senior Software Engineer AI Agent. Your goal is to solve complex coding tasks within this project autonomously and reliably.\n\nOPERATING MODE: ReAct (Thought -> Action -> Observation).\n\nHOW TO WORK:\n1. EXPLORE: Use 'search_files', 'find_by_name', and 'grep_search' to map the project.\n2. ANALYZE: Use 'list_dir' and 'read_file' to understand context.\n3. EXECUTE: Use 'edit_file', 'create_file', 'move_file', or 'delete_file' to implement changes.\n4. VERIFY: Use 'run_command' to ensure everything works.\n\nJSON FORMAT:\n{\n  \"thought\": \"Reasoning...\",\n  \"action\": \"tool_name\",\n  \"params\": {\"arg\": \"val\"}\n}",
            "color": "#00f2ff"
        },
        {
            "id": "architect",
            "name": "Arquitecto de Código",
            "prompt": "You are a Software Architect. You focus on project structure, refactoring, and clean code. Use 'list_dir' and 'move_file' to organize the workspace. Ensure all components are logically placed.",
            "color": "#ffaa00"
        },
        {
            "id": "researcher",
            "name": "Investigador Académico",
            "prompt": "You are a Research Agent. You excel at finding information using 'search_web' and performing deep analysis with 'grep_search'. Your goal is to provide detailed reports and documentation.",
            "color": "#00ff88"
        },
        {
            "id": "security",
            "name": "Auditor de Seguridad",
            "prompt": "You are a Security Specialist. Analyze code for vulnerabilities using 'read_file' and 'grep_search'. Use 'run_command' to execute security scanners or audit tools.",
            "color": "#ff4444"
        },
        {
            "id": "doc_agent",
            "name": "Documentador Técnico",
            "prompt": "You are a Documentation Expert. Keep READMEs, wikis, and docstrings up to date. Use 'read_file' to understand the code and 'edit_file' to improve its documentation.",
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
        "grep_search": True,
        "list_dir": True,
        "find_by_name": True,
        "delete_file": True,
        "move_file": True
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

                # HEURISTIC: Force update "default" prompt and add missing specialized agents
                current_agent_ids = {a.get("id") for a in data.get("agents", [])}
                config_changed = False
                
                for default_agent in DEFAULT_CONFIG["agents"]:
                    if default_agent["id"] not in current_agent_ids:
                        data["agents"].append(default_agent)
                        current_agent_ids.add(default_agent["id"])
                        config_changed = True
                        print(f"Added missing agent: {default_agent['name']}")
                    elif default_agent["id"] == "default":
                        # Always update the default agent prompt to ensure it has the latest tools instructions
                        for a in data["agents"]:
                            if a["id"] == "default":
                                if a.get("prompt") != default_agent["prompt"]:
                                    a["prompt"] = default_agent["prompt"]
                                    config_changed = True
                                break
                
                # Ensure all tools from DEFAULT_CONFIG are present in the loaded data
                if "tools" not in data:
                    data["tools"] = DEFAULT_CONFIG["tools"]
                    config_changed = True
                else:
                    for tool_name, enabled in DEFAULT_CONFIG["tools"].items():
                        if tool_name not in data["tools"]:
                            data["tools"][tool_name] = enabled
                            config_changed = True

                self.config = data
                if config_changed:
                    self.save()
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
