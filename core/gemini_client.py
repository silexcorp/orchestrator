from google import genai
from typing import Generator, List, Dict, Optional

class GeminiClient:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        if api_key:
            self.client = genai.Client(api_key=api_key)

    def chat_stream(self, messages: List[Dict], system: str = None) -> Generator[str, None, None]:
        if not self.api_key:
            yield "Error: No se ha configurado la API KEY de Gemini."
            return
        
        if not self.client:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                yield f"Error inicializando cliente Gemini: {str(e)}"
                return

        # Convert history format for google-genai
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            # google-genai expects "parts" as a list of dictionaries with "text"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        try:
            # Note: system_instruction is passed as part of the config
            config = {}
            if system:
                config["system_instruction"] = system

            response = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # Use a flag to see if we got at least one chunk
            got_content = False
            for chunk in response:
                if chunk.text:
                    got_content = True
                    yield chunk.text
            
            if not got_content:
                yield "Error: Gemini no devolvió ninguna respuesta (posible problema de cuota o contenido bloqueado)."

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                yield "Error 429: Has excedido tu cuota de Gemini. Por favor, revisa tu plan en Google AI Studio o intenta de nuevo en un minuto."
            elif "403" in err_msg:
                yield "Error 403: Acceso denegado. Revisa que tu API KEY sea válida y tenga permisos."
            else:
                yield f"Error en Gemini chat_stream: {err_msg}"

    def is_connected(self) -> bool:
        return bool(self.api_key)
