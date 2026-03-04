# Watchers (Monitores de Carpetas)

Orchestrator Watchers monitorean carpetas en busca de cambios en el sistema de archivos y activan automáticamente tareas de agentes de IA.

---

## Resumen

Los Watchers permiten la automatización basada en eventos. Mientras que los **Schedules** se ejecutan por tiempo, los **Watchers** reaccionan a eventos reales: archivos creados, modificados o eliminados.

Casos de uso comunes:
- **Organización de archivos**: Ordenar y renombrar archivos automáticamente al aparecer.
- **Procesamiento de contenido**: Analizar o resumir documentos cuando se añaden a una carpeta.
- **Flujos de trabajo**: Disparar tareas complejas de IA al soltar archivos en un directorio.

---

## Cómo empezar

### Crear un Watcher
1. Abre la ventana de gestión (**Ctrl + Shift + M**).
2. Ve a la pestaña **Watchers**.
3. Rellena la configuración:
   - **Path**: La ruta absoluta de la carpeta a monitorear.
   - **Recursive**: Marca esta opción si quieres monitorear también las subcarpetas.
4. Haz clic en **Add Watcher**.

---

## Funcionamiento Técnico

### Detección con Watchdog
En Linux, Orchestrator utiliza la librería `watchdog` para monitorear eventos del kernel. Es eficiente y consume pocos recursos.

### Debounce (Anti-rebote)
Orchestrator espera un breve periodo (por defecto 1 segundo) después de detectar cambios antes de activar al agente. Esto evita que el agente se dispare múltiples veces mientras un archivo grande se está copiando o descargando.

### Ciclo de Convergencia
Para evitar bucles infinitos (por ejemplo, si el agente mueve un archivo dentro de la misma carpeta que vigila), Orchestrator incluye lógica para detectar si los cambios fueron causados por la propia aplicación.

---

## Solución de Problemas

### El Watcher no se dispara
- Verifica que la ruta de la carpeta sea correcta y tengas permisos de lectura.
- Asegúrate de que el proceso principal de Orchestrator tenga permisos para acceder a esa ubicación.
- Si el cambio ocurre en una subcarpeta, asegúrate de haber activado la opción **Recursive**.

### El agente se ejecuta demasiadas veces
- Para carpetas con cambios muy frecuentes, considera usar un agente con instrucciones que ignoren archivos ya procesados.
- Verifica que el agente no esté creando nuevos archivos que a su vez disparen el mismo watcher en un bucle.
