# Agents (Autonomous Work)

Orchestrator Agents allow the execution of complex tasks autonomously, with issue tracking, planning, and integrated file operations.

---

## How to Start

### Access
1. In the chat window, select the **Agent** tab.
2. You will see the "Work Mode" interface with a sidebar for task tracking.

### Working Directory
Before an agent performs file operations:
1. Click on **File -> Open Folder** (`Ctrl+Shift+O`).
2. Choose the root directory of your project.
The `WorkspaceManager` will handle setting the root, and the agent will automatically receive a **snapshot** of the project structure and the content of the active file to act with full context.

---

## Key Concepts

### Reasoning Cycle
The agent enters an iterative loop (maximum 30 steps):
1. **Observe**: Analyzes the current state or the result of the last action.
2. **Think**: Determines the next logical step.
3. **Act**: Calls a tool (read file, edit code, execute shell).
4. **Verify**: Evaluates if the step was successful.

### Issue Tracking
Tasks are broken down into "Issues" (pending, in progress, blocked, closed). The agent will update these states automatically as it progresses.

---

## Available Tools

- **Files**: `read_file`, `edit_file`, `create_file`, `list_files`.
- **System**: `run_command` (requires approval if it's a destructive command).
- **Project**: `workspace_snapshot`.

---

## Best Practices

- **Clear instructions**: Be specific ("Add a logout button in the Navbar component" is better than "Fix the UI").
- **Manual control**: You can pause the agent at any time or close execution threads from the management window.
- **History**: All file changes are logged; you can consult them in the session log.
