# Contributing to Orchestrator (Python)

Thank you for your interest in improving Orchestrator for Linux! As it is now a project based on Python and PyQt6, contributing is easier than ever.

## Development Requirements

1. **Python 3.10+**
2. **Ollama** for local testing.
3. **PyQt6** for interface development.

## Environment Setup

1. Clone the repository.
2. Create a virtual environment in `venv`:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Code Structure

- **`core/`**: For backend logic, new inference services, or improvements to the tool execution engine.
- **`ui/`**: For visual changes or new tabs in the settings dialog.
- **`ui/styles.py`**: Contains the global CSS for the application (if applicable).

## Style Guides

- **PEP 8**: We follow standard Python conventions.
- **Modern UI**: Maintain the premium "Deep Space" aesthetic. Use the color tokens defined in the styling system.
- **Threads**: Any network or inference operation must run in a separate thread to avoid blocking the interface (see `Agent` as an example).

## Bug Reporting

If you find an error, please open an Issue detailing:
1. Your Linux distribution.
2. Python and Ollama versions.
3. The error traceback if available.

---

Orchestrator is an open-source project under the GPL-3.0 license.
