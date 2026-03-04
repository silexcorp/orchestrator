# IDE Mode and Workspace Management 🖥️

Orchestrator includes an advanced editing mode that transforms the chat into an Integrated Development Environment (IDE).

## The Workspace

The "Workspace" is the heart of the agent's workflow. Upon opening a folder:

1.  **Exploration**: The sidebar with the file tree is activated.
2.  **Context**: The agent generates a `Project Snapshot` that includes:
    *   The hierarchical file structure.
    *   The content of the file you currently have open.
    *   Quick views of relevant project files.
3.  **Terminal**: The integrated terminal automatically sets its working directory (`CWD`) to the root of the opened folder.

## Multi-Tab Editor

The code editor now supports multiple files through tabs:

*   **Change Indicators**: A circle (●) on the tab indicates that the file has unsaved changes.
*   **Shortcuts**:
    *   `Ctrl+S`: Save active file.
    *   `Ctrl+W`: Close current tab.
    *   `Ctrl+Tab`: Navigate between open tabs.
*   **Smart Opening**: If the agent attempts to edit a file you already have open, the editor will simply switch focus to that tab instead of duplicating it.

## Session Persistence

Orchestrator remembers your work pace. When closing the program, it is automatically saved in `~/.orchestrator_ai/session.json`:

*   The last opened workspace.
*   The list of files you had in tabs.
*   **Provider Choice**: Remembers whether you prefer **Ollama** or **Gemini** via a dedicated toggle.
*   **Model Selection**: Remembers the specific local model or the remote Gemini version.
*   The size and position of panels (Splitters).
*   **Panel Visibility**: Preferences for showing/hiding the File Explorer, Terminal, Log Panel, and Chat History Sidebar.

## Multi-Chat & Conversation Persistence

Orchestrator now supports multiple independent chat sessions. Each session is a standalone context:
- **Independent Histories**: The agent's knowledge of the conversation is saved per-chat.
- **Auto-Titling**: New chats are automatically named based on your first input for easy organization.
- **Full History Storage**: Assistant thoughts, tool executions, and observations are all persisted.
- **Location**: Conversations are stored as JSON files in `~/.orchestrator_ai/chats/`.

## Layout & Splitting

The agent has access to specialized tools to navigate the project:

*   `list_files`: Allows the agent to search for specific files using patterns (e.g., `*.py`).
*   `read_file`: The agent can read any project file to obtain more context than initially sent.
*   `create_file` / `edit_file`: Capability to make changes directly in the code.

---
---
## Advanced Rendering

In any mode, Orchestrator provides:
- **Math Visualization**: High-fidelity **LaTeX** rendering for technical responses.
- **Syntax Highlighting**: Beautiful code blocks with Monokai styling.

*Note: IDE mode is fully compatible with both local Ollama and remote Google Gemini.*
