import ollama
from typing import Generator, List, Optional

class OllamaClient:
    def __init__(self, model: Optional[str] = None):
        self.model = model

    def set_model(self, model_name: str):
        self.model = model_name

    def list_models(self) -> List[str]:
        try:
            response = ollama.list()
            models = []
            for m in response.models:
                if hasattr(m, 'model'):
                    models.append(m.model)
                elif isinstance(m, dict) and 'name' in m:
                    models.append(m['name'])
                elif isinstance(m, dict) and 'model' in m:
                    models.append(m['model'])
            return models
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def chat_stream(self, messages: List[dict], system: str = None) -> Generator[str, None, None]:
        if not self.model:
            yield "Error: No se ha seleccionado ningún modelo en la interfaz."
            return
        msgs = []
        if system:
            msgs.append({'role': 'system', 'content': system})
        msgs.extend(messages)
        
        try:
            stream = ollama.chat(
                model=self.model,
                messages=msgs,
                stream=True,
            )
            for chunk in stream:
                yield chunk['message']['content']
        except Exception as e:
            yield f"Error in chat_stream: {str(e)}"

    def is_connected(self) -> bool:
        try:
            ollama.list()
            return True
        except:
            return False
