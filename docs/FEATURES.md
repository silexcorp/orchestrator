# Funcionalidades de Orchestrator (Python/Linux)

Referencia de las capacidades actuales de la versión Python de Orchestrator.

## Matriz de Funcionalidades

| Funcionalidad | Estado | Descripción |
| :--- | :--- | :--- |
| **Chat con Ollama** | Estable | Inferencia local optimizada mediante la API de Ollama. |
| **Proveedores Remotos**| Estable | Soporte para OpenAI, Anthropic, OpenRouter y xAI. |
| **Servidor MCP** | Estable | API compatible con OpenAI para conectar otras apps de IA. |
| **Agentes** | Estable | Perfiles personalizados con prompts de sistema y temas. |
| **Memory** | Estable | Búsqueda por palabras clave (BM25) y perfiles de usuario. |
| **Schedules** | Estable | Tareas automáticas programadas mediante expresiones CRON. |
| **Watchers** | Estable | Monitoreo de cambios en carpetas para disparar acciones. |
| **Skills** | Estable | Importación de lógica de IA desde archivos Markdown. |
| **Work Mode** | Estable | Orquestador de tareas multi-paso (Agentes autónomos). |
| **Insights** | Estable | Registro de velocidad (tokens/s), latencia y éxito de inferencia. |
| **Workspace (IDE)** | Estable | Apertura de carpetas, árbol de archivos y contexto dinámico. |
| **Multi-Tab Editor**| Estable | Soporte para múltiples archivos con pestañas y resaltado. |
| **Persistencia** | Estable | Guardado automático del estado de la sesión (tabs, layout). |

---

## Detalles de Arquitectura

La aplicación está dividida en tres capas principales:

1. **Modelos (`orchestrator/models/`)**: Definiciones de datos compartidas (Agentes, Sesiones, Proveedores).
2. **Core (`core/`)**: Lógica de negocio, servicios de inferencia, gestión de workspaces (`workspace.py`) y persistencia (`session.py`).
3. **UI (`ui/`)**: Interfaz gráfica construida con PyQt6, incluyendo el `EditorWidget` (tabs) y `FileTreeWidget`.

---

## Local vs Remoto

### Ollama (Local)
Orchestrator se comunica con el servidor de Ollama (`localhost:11434`). Permite descargar, borrar y listar modelos directamente desde la interfaz de gestión.

### Remote Providers (Nube)
Configura tus API Keys para usar Claude (Anthropic), GPT-4 (OpenAI) o cualquier modelo disponible en OpenRouter. Orchestrator unifica estas APIs para que el chat sea agnóstico al proveedor.

---

## Automatización

### Watchers
Utiliza la librería `watchdog` para detectar cambios en el sistema de archivos. Cuando un archivo es creado o modificado en una carpeta vigilada, puedes configurar un agente para que procese esa información automáticamente.

### Schedules
Permite ejecutar promts de manera recurrente. Ideal para reportes diarios, resúmenes de noticias o tareas de mantenimiento de datos.

---

## Servidor MCP

Orchestrator puede actuar como un puente para otras aplicaciones. Al activar el servidor, este expone un endpoint compatible con la especificación de Chat Completions de OpenAI. Esto permite usar tus agentes y modelos locales de Orchestrator en herramientas como Cursor o extensiones de VS Code.
