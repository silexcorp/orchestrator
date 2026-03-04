# Shared Configuration (Linux)

Orchestrator on Linux uses a centralized directory to save all its configuration and persistent data.

## File Location

By default, everything is saved in:
`~/.orchestrator_ai/`

### Key Files

| File | Description |
| :--- | :--- |
| **`config.json`** | Main configuration file. Includes agent profiles, tools state, and preferred models. |
| **`session.json`**| Stores the state of the last session (open tabs, workspace path, window layout). |

## Manual Editing

While it is recommended to use the **Settings (Ctrl+,)** interface, JSON files can be edited manually. Ensure Orchestrator is closed before editing them to prevent changes from being overwritten by the program upon exit.

## Virtual Environment

The application runs within a virtual environment located in the project root:
`venv/`

To install new libraries manually:
```bash
./venv/bin/pip install <library>
```
