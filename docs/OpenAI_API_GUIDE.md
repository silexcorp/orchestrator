# Orchestrator API Guide

Orchestrator exposes an OpenAI-compatible API that allows you to integrate your local and remote models into other applications.

## Available Endpoints

### 1. List Models - `GET /v1/models`

Returns available models (both local from Ollama and configured remote providers).

```bash
curl http://127.0.0.1:8080/v1/models
```

### 2. Chat Completions - `POST /v1/chat/completions`

Generates responses using the specified model. Supports streaming.

#### Request Example (Streaming)

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [
      {"role": "user", "content": "Hello, who are you?"}
    ],
    "stream": true,
    "temperature": 0.7
  }'
```

## Integration with Official Libraries

You can use the official OpenAI SDK by pointing to the Orchestrator server:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": "Tell me a joke"}]
)

print(response.choices[0].message.content)
```

## Server Configuration

The server is controlled from the **Server** tab in the application's management window.
- **Default Port**: 8080
- **Host**: 127.0.0.1 (Localhost)

---

## Technical Notes

- **Ollama**: Ensure Ollama is running for local models to respond correctly.
- **Remote Providers**: The Orchestrator API will act as a proxy, using the API Keys you have configured in the application.
- **Performance**: Response speed depends on your local hardware (for Ollama) or your internet connection (for remotes).
