# Guía de API de Orchestrator

Orchestrator expone una API compatible con OpenAI que permite integrar tus modelos locales y remotos en otras aplicaciones.

## Endpoints Disponibles

### 1. Listar Modelos - `GET /v1/models`

Devuelve los modelos disponibles (tanto locales de Ollama como proveedores remotos configurados).

```bash
curl http://127.0.0.1:8080/v1/models
```

### 2. Chat Completions - `POST /v1/chat/completions`

Genera respuestas utilizando el modelo especificado. Soporta streaming.

#### Ejemplo de Petición (Streaming)

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [
      {"role": "user", "content": "Hola, ¿quién eres?"}
    ],
    "stream": true,
    "temperature": 0.7
  }'
```

## Integración con Librerías Oficiales

Puedes usar el SDK oficial de OpenAI apuntando al servidor de Orchestrator:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": "Dime un chiste"}]
)

print(response.choices[0].message.content)
```

## Configuración del Servidor

El servidor se controla desde la pestaña **Server** en la ventana de gestión.
- **Puerto por defecto**: 8080
- **Host**: 127.0.0.1 (Localhost)

---

## Notas Técnicas

- **Ollama**: Asegúrate de que Ollama esté corriendo para que los modelos locales respondan correctamente.
- **Proveedores Remotos**: La API de Orchestrator actuará como proxy, usando las API Keys que hayas configurado en la aplicación.
- **Rendimiento**: La velocidad de respuesta depende de tu hardware local (para Ollama) o de tu conexión a internet (para remotos).
