import json
import os
from typing import Dict, List, Optional

class SessionManager:
    def __init__(self):
        # Align with ConfigManager directory
        self.session_dir = os.path.expanduser("~/.orchestrator_ai")
        self.session_file = os.path.join(self.session_dir, "session.json")
        self.chats_dir = os.path.join(self.session_dir, "chats")
        
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)
        if not os.path.exists(self.chats_dir):
            os.makedirs(self.chats_dir)

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

    # --- Workspace management ---
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

    # --- Multi-Chat management ---
    def get_chats(self) -> List[Dict]:
        """Returns a list of chat metadata (id, title, timestamp)."""
        chats = []
        if not os.path.exists(self.chats_dir):
            return chats
            
        for filename in os.listdir(self.chats_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.chats_dir, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        chats.append({
                            "id": data.get("id"),
                            "title": data.get("title", "New Chat"),
                            "updated_at": data.get("updated_at", 0)
                        })
                except:
                    continue
        
        # Sort by most recent
        chats.sort(key=lambda x: x["updated_at"], reverse=True)
        return chats

    def save_chat(self, chat_id: str, history: List[Dict], title: str = None):
        import time
        path = os.path.join(self.chats_dir, f"{chat_id}.json")
        
        # Try to keep existing title if not provided
        if not title and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    old_data = json.load(f)
                    title = old_data.get("title")
            except: pass
            
        data = {
            "id": chat_id,
            "title": title or (history[0]["content"][:30] + "..." if history else "New Chat"),
            "history": history,
            "updated_at": time.time()
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_chat(self, chat_id: str) -> Optional[Dict]:
        path = os.path.join(self.chats_dir, f"{chat_id}.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    def delete_chat(self, chat_id: str):
        path = os.path.join(self.chats_dir, f"{chat_id}.json")
        if os.path.exists(path):
            os.remove(path)
