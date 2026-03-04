import json
import os
from typing import Dict, List, Optional

class SessionManager:
    def __init__(self):
        self.session_dir = os.path.expanduser("~/.nova_editor")
        self.session_file = os.path.join(self.session_dir, "session.json")
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)

    def save(self, state: Dict):
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")

    def load(self) -> Dict:
        if not os.path.exists(self.session_file):
            return {}
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return {}

    def add_recent_workspace(self, path: str):
        state = self.load()
        recent = state.get("recent_workspaces", [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        state["recent_workspaces"] = recent[:10]
        self.save(state)

    def get_recent_workspaces(self) -> List[str]:
        return self.load().get("recent_workspaces", [])
