# Orchestrator Features (Python/Linux)

Reference of the current capabilities of the Python version of Orchestrator.

## Feature Matrix

| Feature | Status | Description |
| :--- | :--- | :--- |
| **Chat with Ollama** | Stable | Local inference optimized via the Ollama API. |
| **Remote Providers**| Stable | Support for OpenAI, Anthropic, OpenRouter, and xAI. |
| **MCP Server** | Stable | OpenAI-compatible API to connect other AI apps. |
| **Agents** | Stable | Custom profiles with system prompts and themes. |
| **Search (Web)** | Stable | Integrated Brave Search API for live internet access. |
| **Multi-Chat** | Stable | Sidebar with independent sessions and auto-titling. |
| **Memory** | Stable | Keyword search (BM25) and user profiles. |
| **Schedules** | Stable | Automated tasks scheduled via CRON expressions. |
| **Watchers** | Stable | Folder monitoring to trigger automatic actions. |
| **Skills** | Stable | Import AI logic from Markdown files. |
| **Work Mode** | Stable | Multi-step task orchestrator (Autonomous Agents). |
| **Insights** | Stable | Logs for speed (tokens/s), latency, and inference success. |
| **Workspace (IDE)** | Stable | Folder opening, file tree, and dynamic context. |
| **Multi-Tab Editor**| Stable | Support for multiple files with tabs and highlighting. |
| **Persistence** | Stable | Full session state saving including chat history. |
| **Temporal Data** | Stable | Awareness of current date, time, and OS environment. |
| **VRAM Optimization**| Stable | Automatic model unloading on close to free up GPU. |
| **Robust JSON** | Stable | Structural repair for truncated or malformed responses. |
| **Settings** | Stable | Full management of profiles, models, and tools (`Ctrl+,`). |
| **Antigravity UI** | Stable | Premium "Deep Space" interface with cyan/purple accents. |

---

## Architecture Details

The application is divided into three main layers:

1. **Models (`orchestrator/models/`)**: Shared data definitions (Agents, Sessions, Providers).
2. **Core (`core/`)**: Business logic, inference services, workspace management (`workspace.py`), and persistence (`session.py`).
3. **UI (`ui/`)**: Graphic interface built with PyQt6, including the `EditorWidget` (tabs), `FileTreeWidget`, and the new `LogPanel`. See [Antigravity Design](ANTIGRAVITY_DESIGN.md).

---

## Local vs Remote

### Ollama (Local)
Orchestrator communicates with the Ollama server (`localhost:11434`). It allows downloading, deleting, and listing models directly from the management interface.

### Remote Providers (Cloud)
Configure your API Keys to use Claude (Anthropic), GPT-4 (OpenAI), or any model available on OpenRouter. Orchestrator unifies these APIs so the chat is provider-agnostic.

---

## Automation

### Watchers
Uses the `watchdog` library to detect filesystem changes. When a file is created or modified in a watched folder, you can configure an agent to process that information automatically.

### Schedules
Allows executing prompts on a recurring basis. Ideal for daily reports, news summaries, or data maintenance tasks.

---

## MCP Server

Orchestrator can act as a bridge for other applications. When activating the server, it exposes an endpoint compatible with the OpenAI Chat Completions specification. This allows using your local Orchestrator agents and models in tools like Cursor or VS Code extensions.
