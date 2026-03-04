# Orchestrator (Linux)

Orchestrator es un runtime de IA ligero y potente para Linux, reimplementado en Python para ofrecer una experiencia nativa y fluida. Permite ejecutar modelos locales y remotos, automatizar tareas mediante agentes y exponer herramientas a través del protocolo MCP.

Reimplementado de Swift a Python con PyQt6 y Ollama.

<img src="https://github.com/silexcorp/orchestrator/blob/master/screenshot/page.png" width="900">

## Características principales

- **Inferencia Local con Ollama** — Soporte para Llama, Qwen, Gemma, Mistral y más.
- **Proveedores Remotos** — Conexión nativa a Anthropic, OpenAI, OpenRouter u otros proveedores compatibles con OpenAI.
- **Servidor MCP** — Expone herramientas a agentes de IA mediante el Model Context Protocol.
- **Interfaz Premium** — UI moderna construida con PyQt6, optimizada para Linux.
- **Automatización**:
    - **Schedules**: Tareas programadas por tiempo (CRON).
    - **Watchers**: Monitoreo de carpetas con disparadores automáticos.
    - **Skills**: Importación de capacidades de IA en Markdown.
- **Memoria Persistente**: Perfil de usuario, memoria de trabajo y búsqueda BM25.

## Requisitos

- **Linux** (Probado en Ubuntu 24.04+)
- **Python 3.10+**
- **Ollama** (`ollama serve` debe estar corriendo)

## Instalación

Orchestrator utiliza un entorno virtual para evitar conflictos con el sistema:

```bash
# Entrar al directorio
cd orchestrator

# Crear el entorno virtual
python3 -m venv venv

# Instalar dependencias
./venv/bin/pip install -r requirements.txt
```

## Ejecución

Para lanzar la aplicación:

```bash
cd ..
./orchestrator/venv/bin/python3 -m orchestrator.main
```

## Configuración

Los datos y la configuración se guardan en `~/.config/orchestrator/`:
- `agents.json`: Configuración de asistentes.
- `providers.json`: API Keys y endpoints remotos.
- `sessions.json`: Historial de chats.
- `insights.json`: Logs de rendimiento.
- `skills/`: Habilidades personalizadas en Markdown.

---

## Documentación Detallada

- [Funcionalidades](docs/FEATURES.md)
- [Guía de Configuración](docs/SHARED_CONFIGURATION_GUIDE.md)
- [Memoria y Contexto](docs/MEMORY.md)
- [Automatización (Watchers)](docs/WATCHERS.md)
- [Trabajo con Agentes (Work)](docs/WORK.md)

---

Creado originalmente por Dinoki Labs y portado a Linux/Python por Antigravity.
