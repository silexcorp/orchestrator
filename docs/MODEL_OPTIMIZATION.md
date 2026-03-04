# Model Optimization and Response Robustness

Orchestrator includes advanced mechanisms for efficient resource management and resilience in communication with local models (Ollama).

## 1. Automatic Memory Release (VRAM/RAM)

To maximize system performance, Orchestrator ensures it does not leave models "hanging" in memory after the application is closed.

### How it Works
- Upon detecting the closure event (`closeEvent`), the Ollama client sends a request with the parameter `keep_alive: 0`.
- This instructs the Ollama server to unload the model immediately from GPU tensors or RAM.
- **Benefit**: The system recovers gigabytes of memory instantly for other applications.

## 2. Robust JSON Parsing and Structural Repair

Local models can sometimes generate malformed responses due to quantization or unexpected stops. Orchestrator implements a resilient JSON extraction engine.

### Repair Capabilities
- **Trailing Commas**: Automatically removes extra commas at the end of objects or lists, which typically break the JSON standard.
- **Structure Balancing**: If a response is cut off prematurely (truncation), the engine counts open braces `{` and brackets `[` and adds the corresponding closures `}` `]` to attempt to save as much of the message as possible.
- **Smart Extraction**: Searches for Markdown code block patterns (```json) and, failing that, uses a search algorithm for first and last delimiters.

## 3. System Prompt Configuration

The agent's "brain" has been reinforced with specific instructions to minimize formatting errors:
- Mandatory strict JSON format.
- Prohibition of including unnecessary control characters or trailing commas.
