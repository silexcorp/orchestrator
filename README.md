# Orchestrator AI Code Editor 🦕

Orchestrator is a powerful, agentic AI code editor for Linux, built with PyQt6 and powered by Ollama. It provides a seamless development experience with an integrated AI agent capable of understanding project context, editing files, and running terminal commands.

<img src="https://github.com/silexcorp/orchestrator/blob/master/screenshot/page.png" width="900">

## ✨ Features

- **Agentic AI Core**: A ReAct-based agent that reasons, acts, and observes. It can create/edit files, list directories, and execute shell commands.
- **Dynamic Context Awareness**: The agent automatically receives a "snapshot" of your workspace, including file structure and active file content.
- **Multi-Tab Editor**: Edit multiple files simultaneously with syntax highlighting, line numbers, and unsaved change detection (dirty indicators).
- **Workspace Management**: Open entire folders as projects. The file tree sidebar allows easy navigation and real-time filesystem monitoring via `watchdog`.
- **Integrated Terminal**: Run commands directly within the editor with real-time output.
- **Model Memory Optimization**: Automatically unloads models from GPU/RAM upon application closure, freeing up system resources.
- **Robust JSON Parsing**: Advanced agent response extraction with structural repair logic to handle truncated or malformed JSON from models.
- **Session Persistence**: Automatically restores your last workspace, open tabs, window layout, and preferred Ollama model.
- **Modern Dark Theme**: High-contrast UI inspired by GitHub's dark mode.
- **Model Selector**: Switch between local Ollama models on the fly.

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Ollama**: [Install Ollama](https://ollama.ai/download) and ensure it's running (`ollama serve`).
- **Required Models**: We suggest `qwen2.5-coder:7b` or `qwen3.5:9b`.

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

### Running the Editor

```bash
./venv/bin/python3 main.py
```

## 🛠️ Architecture

- **`core/`**:
  - `agent.py`: The AI brain (ReAct loop).
  - `tools.py`: File and command execution tools.
  - `workspace.py`: Context snapshot and file management.
  - `session.py`: JSON-based state persistence.
  - `ollama_client.py`: Wrapper for the Ollama API.
- **`ui/`**:
  - `main_window.py`: Layout integration and signal orchestration.
  - `editor_widget.py`: Tabbed code editor with syntax highlighting.
  - `file_tree.py`: Sidebar for project navigation.
  - `chat_widget.py`: Specialized chat with thought/action/observation bubbles.
  - `terminal_widget.py`: Integrated shell access.

## ⌨️ Shortcuts

- `Ctrl+S`: Save current file.
- `Ctrl+Shift+O`: Open folder (Workspace).
- `Ctrl+W`: Close current tab.
- `Ctrl+Tab`: Switch between tabs.
- `Enter`: Send message in chat.
- `Shift+Enter`: New line in chat.

## 📄 License

GPL-3.0 License. See `LICENSE` for details.
