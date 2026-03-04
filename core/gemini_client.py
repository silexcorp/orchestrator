import google.generativeai as genai
from typing import Generator, List, Optional

class GeminiClient:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)

    def chat_stream(self, messages: List[dict], system: str = None) -> Generator[str, None, None]:
        if not self.api_key:
            yield "Error: No se ha configurado la API KEY de Gemini."
            return
        
        if not self.model:
             self.model = genai.GenerativeModel(self.model_name)

        # Convert history format
        # Orchestrator uses: {"role": "user"|"assistant", "content": "..."}
        # Gemini uses: {"role": "user"|"model", "parts": ["..."]}
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        
        try:
            chat = self.model.start_chat(history=history)
            
            # Append system prompt instructions to the last message or use specialized config
            last_msg = messages[-1]["content"]
            prompt = last_msg
            if system:
                prompt = f"System Instructions:\n{system}\n\nUser Request: {last_msg}"

            response = chat.send_message(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"Error in Gemini chat_stream: {str(e)}"

    def is_connected(self) -> bool:
        return bool(self.api_key)
