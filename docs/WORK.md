# Agentes (Trabajo Autónomo)

Los Agentes de Orchestrator permiten la ejecución de tareas complejas de forma autónoma, con seguimiento de problemas (issues), planificación y operaciones de archivos integradas.

---

## Cómo empezar

### Acceso
1. En la ventana de chat, selecciona la pestaña **Agent**.
2. Verás la interfaz de "Work Mode" con un panel lateral para el seguimiento de tareas.

### Directorio de Trabajo
Antes de que un agente realice operaciones de archivos:
1. Haz clic en **Select Folder**.
2. Elige el directorio raíz de tu proyecto.
Orchestrator solo podrá leer y escribir archivos dentro de este directorio seleccionado.

---

## Conceptos Clave

### Ciclo de Razonamiento
El agente entra en un bucle iterativo (máximo 30 pasos):
1. **Observa**: Analiza el estado actual o el resultado de la última acción.
2. **Piensa**: Determina el siguiente paso lógico.
3. **Actúa**: Llama a una herramienta (leer archivo, editar código, ejecutar shell).
4. **Verifica**: Evalúa si el paso fue exitoso.

### Seguimiento de Issues
Las tareas se desglosan en "Issues" (pendientes, en progreso, bloqueadas, cerradas). El agente actualizará estos estados automáticamente a medida que avance.

---

## Herramientas Disponibles

- **Archivos**: `file_read`, `file_edit`, `file_write`, `file_search`, `file_tree`.
- **Sistema**: `shell_run` (requiere aprobación si es comando destructivo), `dir_create`.
- **Git**: `git_status`, `git_diff`, `git_commit`.

---

## Mejores Prácticas

- **Instrucciones claras**: Sé específico ("Añade un botón de logout en el componente Navbar" es mejor que "Arregla la UI").
- **Control manual**: Puedes pausar al agente en cualquier momento o cerrar hilos de ejecución desde la ventana de gestión.
- **Historial**: Todos los cambios de archivos quedan registrados; puedes consultarlos en el log de la sesión.
