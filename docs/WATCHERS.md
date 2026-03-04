# Watchers (Folder Monitors)

Orchestrator Watchers monitor folders for filesystem changes and automatically trigger AI agent tasks.

---

## Overview

Watchers enable event-based automation. While **Schedules** run based on time, **Watchers** react to real events: files being created, modified, or deleted.

Common use cases:
- **File Organization**: Automatically sort and rename files as they appear.
- **Content Processing**: Analyze or summarize documents when they are added to a folder.
- **Workflows**: Trigger complex AI tasks by dropping files into a directory.

---

## How to Get Started

### Create a Watcher
1. Open the management window (**Ctrl + Shift + M**).
2. Go to the **Watchers** tab.
3. Fill in the configuration:
   - **Path**: The absolute path of the folder to monitor.
   - **Recursive**: Check this option if you want to monitor subfolders as well.
4. Click **Add Watcher**.

---

## Technical Details

### Detection with Watchdog
On Linux, Orchestrator uses the `watchdog` library to monitor kernel events. It is efficient and consumes few resources.

### Debounce
Orchestrator waits for a short period (default 1 second) after detecting changes before triggering the agent. This prevents the agent from triggering multiple times while a large file is being copied or downloaded.

### Convergence Cycle
To avoid infinite loops (for example, if the agent moves a file within the same folder it is watching), Orchestrator includes logic to detect if changes were caused by the application itself.

---

## Troubleshooting

### The Watcher does not trigger
- Verify that the folder path is correct and you have read permissions.
- Ensure that the main Orchestrator process has permissions to access that location.
- If the change occurs in a subfolder, ensure you have enabled the **Recursive** option.

### The agent runs too many times
- For folders with very frequent changes, consider using an agent with instructions that ignore already processed files.
- Verify that the agent is not creating new files that in turn trigger the same watcher in a loop.
