# Contribuyendo a Orchestrator (Python)

¡Gracias por tu interés en mejorar Orchestrator para Linux! Al ser ahora un proyecto basado en Python y PyQt6, contribuir es más sencillo que nunca.

## Requisitos de Desarrollo

1. **Python 3.10+**
2. **Ollama** para pruebas locales.
3. **PyQt6** para el desarrollo de la interfaz.

## Configuración del Entorno

1. Clona el repositorio.
2. Crea un entorno virtual en `orchestrator/venv`:
   ```bash
   cd orchestrator
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Estructura del Código

- **`orchestrator/models/`**: Si necesitas añadir nuevos datos o campos persistentes.
- **`orchestrator/core/`**: Para lógica de backend, nuevos servicios de inferencia o mejoras en el motor MCP.
- **`orchestrator/ui/`**: Para cambios visuales o nuevas pestañas en la ventana de gestión.
- **`orchestrator/styles.py`**: Contiene el CSS global de la aplicación.

## Guías de Estilo

- **PEP 8**: Seguimos las convenciones estándar de Python.
- **Modern UI**: Mantén la estética "Dark/Purple" premium. Usa los tokens de color definidos en `styles.py`.
- **Hilos**: Cualquier operación de red o inferencia debe ejecutarse en un hilo separado para no bloquear la interfaz (ver `ChatEngine` como ejemplo).

## Reporte de Bugs

Si encuentras un error, por favor abre un Issue detallando:
1. Tu distribución de Linux.
2. Versión de Python y Ollama.
3. El traceback del error si está disponible.

---

Orchestrator es un proyecto de código abierto bajo la licencia MIT.
