# Configuración Compartida (Linux)

Orchestrator en Linux utiliza el directorio estándar de XDG para guardar toda su configuración y datos persistentes.

## Ubicación de archivos

Por defecto, todo se guarda en:
`~/.config/orchestrator/`

### Archivos clave

| Archivo | Descripción |
| :--- | :--- |
| **`agents.json`** | Lista de agentes configurados, incluyendo sus prompts, modelos por defecto y temas visuales. |
| **`providers.json`** | Configuración de proveedores remotos (API Keys, URLs base de OpenAI/Anthropic). |
| **`sessions.json`** | Historial de conversaciones locales. |
| **`insights.json`** | Logs de rendimiento de las últimas 500 inferencias. |
| **`memory_entries.json`**| Entradas de memoria de trabajo extraídas de los chats. |
| **`user_profiles.json`** | Resúmenes de perfiles de usuario por agente. |
| **`skills/`** | Carpeta que contiene archivos `.md` de habilidades importadas. |

## Edición Manual

Aunque se recomienda usar la interfaz de **Management (Ctrl+Shift+M)**, los archivos JSON pueden editarse manualmente. Asegúrate de cerrar Orchestrator antes de editarlos para evitar que los cambios sean sobrescritos por el programa al salir.

## Entorno Virtual

La aplicación se ejecuta dentro de un entorno virtual localizado en:
`orchestrator/venv/`

Para instalar nuevas librerías manualmente:
```bash
./orchestrator/venv/bin/pip install <libreria>
```
