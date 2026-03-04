# Orchestrator AI 🦕

Orchestrator is a powerful, agentic AI code editor for Linux, built with PyQt6 and powered by Ollama. It provides a seamless development experience with an integrated AI agent capable of understanding project context, editing files, and running terminal commands.

<img src="https://github.com/silexcorp/orchestrator/blob/master/screenshot/page.png" width="900">

## ✨ Features

- **Agentic AI Core**: A ReAct-based agent that reasons, acts, and observes. It can create/edit files, list directories, and execute shell commands.
- **Google Gemini Integration**: Use Google's latest models as the primary brain. Configure your API key in settings for a supercharged experience.
- **Provider Selection Toggle**: Easily switch between local Ollama and cloud Gemini without manual configuration changes.
- **Enhanced Chat Rendering**: Support for **LaTeX math formulas** (Arithmatex) and **Syntax Highlighting** (CodeHilite) with Monokai styling.
- **Brave Search Integration**: Connected to the internet via Brave Search API. Use the agent to find latest docs, news, or technical solutions.
- **Workspace Management**: Open entire folders as projects. The file tree sidebar allows easy navigation and real-time filesystem monitoring via `watchdog`.
- **Integrated Terminal**: Run commands directly within the editor with real-time output.
- **Model Memory Optimization**: Automatically unloads models from GPU/RAM upon application closure, freeing up system resources.
- **Robust JSON Parsing**: Advanced agent response extraction with structural repair logic to handle truncated or malformed JSON from models.
- **Session Persistence**: Automatically restores your last workspace, open tabs, window layout, and preferred Ollama model.
- **Agent Log Panel**: Real-time activity log in the bottom right, monitoring "Neural Thoughts", Actions, and Sensor Data.
- **Dynamic Agent Profiles & Settings**: Create and edit multiple agent personalities via the new "Edit -> Settings" menu.
- **Chat Aesthetic**: Premium "Deep Space" visual identity with vibrant cyan/purple accents, responsive chat, and glowing capsule-style input.
- **Model Selector**: Switch between local Ollama models on the fly.

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Ollama**: [Install Ollama](https://ollama.ai/download) for local inference.
- **Google AI SDK**: `google-genai` for remote Gemini support.
- **Required Models**: Local (`qwen3.5:4b`) or Remote (`gemini-2.0-flash`).

### Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd orchestrator
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Ensure `PyQt6`, `ollama`, and `watchdog` are installed.*

### Running the Editor (Development)

```bash
./venv/bin/python3 main.py
```

### 📦 Building the Executable

You can generate a standalone executable for Linux using the provided build script:

```bash
chmod +x build_executable.sh
./build_executable.sh
```

The resulting binary will be located in the `dist/` folder as `Orchestrator`.

## 🛠️ Architecture

- **`core/`**:
  - `agent.py`: The AI brain (ReAct loop).
  - `config.py`: Centralized configuration management and persistence.
  - `tools.py`: File and command execution tools.
  - `workspace.py`: Context snapshot and file management.
  - `session.py`: JSON-based state persistence.
  - `ollama_client.py`: Wrapper for local Ollama API.
  - `gemini_client.py`: Client for the latest Google GenAI SDK.
- **`ui/`**:
  - `main_window.py`: Layout integration and signal orchestration.
  - `settings_dialog.py`: Multi-tab interface for managing agents and tools.
  - `editor_widget.py`: Tabbed code editor with syntax highlighting.
  - `file_tree.py`: Sidebar for project navigation.
  - `chat_widget.py`: Specialized chat with thought/action/observation bubbles.
  - `terminal_widget.py`: Integrated shell access.

## ⌨️ Shortcuts

- `Ctrl+S`: Save current file.
- `Ctrl+Shift+O`: Open folder (Workspace).
- `Ctrl+,`: Open Settings Dialog.
- `Ctrl+W`: Close current tab.
- `Ctrl+Tab`: Switch between tabs.
- `Enter`: Send message in chat.
- `Shift+Enter`: New line in chat.

## 📄 License

GPL-3.0 License. See `LICENSE` for details.

---
We are Okan Team