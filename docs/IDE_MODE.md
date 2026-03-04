# Modo IDE y Gestión de Workspace 🖥️

Orchestrator incluye un modo de edición avanzada que transforma el chat en un entorno de desarrollo integrado (IDE).

## El Workspace

El "Workspace" es el corazón del flujo de trabajo del agente. Al abrir una carpeta:

1.  **Exploración**: Se activa el panel lateral con el árbol de archivos.
2.  **Contexto**: El agente genera un `Project Snapshot` que incluye:
    *   La estructura jerárquica de archivos.
    *   El contenido del archivo que tengas abierto actualmente.
    *   Vistas rápidas de archivos relevantes del proyecto.
3.  **Terminal**: La terminal integrada establece automáticamente su directorio de trabajo (`CWD`) en la raíz de la carpeta abierta.

## Editor Multitabs

El editor de código ahora soporta múltiples archivos mediante pestañas:

*   **Puntos de Cambio**: Un círculo (●) en la pestaña indica que el archivo tiene cambios sin guardar.
*   **Atajos**:
    *   `Ctrl+S`: Guardar archivo activo.
    *   `Ctrl+W`: Cerrar pestaña actual.
    *   `Ctrl+Tab`: Navegar entre pestañas abiertas.
*   **Apertura Inteligente**: Si el agente intenta editar un archivo que ya tienes abierto, el editor simplemente cambiará el foco a esa pestaña en lugar de duplicarla.

## Persistencia de Sesión

Orchestrator recuerda tu ritmo de trabajo. Al cerrar el programa, se guarda automáticamente en `~/.nova_editor/session.json`:

*   El último workspace abierto.
*   La lista de archivos que tenías en pestañas.
*   El modelo de Ollama que estabas usando.
*   El tamaño y posición de los paneles (Splitters).

## Herramientas del Agente para el Workspace

El agente tiene acceso a herramientas especializadas para navegar por el proyecto:

*   `list_files`: Permite al agente buscar archivos específicos mediante patrones (ej: `*.py`).
*   `read_file`: El agente puede leer cualquier archivo del proyecto para obtener más contexto del que se le envía inicialmente.
*   `write_file` / `edit_file`: Capacidad para realizar cambios directamente en el código.

---
*Nota: Este modo requiere tener Ollama instalado y corriendo para que el agente pueda razonar sobre el código.*
