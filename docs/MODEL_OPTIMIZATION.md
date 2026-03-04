# Optimización de Modelos y Robustez de Respuesta

Orchestrator incluye mecanismos avanzados para la gestión eficiente de recursos y la resiliencia en la comunicación con modelos locales (Ollama).

## 1. Liberación Automática de Memoria (VRAM/RAM)

Para maximizar el rendimiento del sistema, Orchestrator se asegura de no dejar modelos "colgados" en la memoria después de cerrar la aplicación.

### Funcionamiento
- Al detectar el evento de cierre (`closeEvent`), el cliente de Ollama envía una solicitud con el parámetro `keep_alive: 0`.
- Esto instruye al servidor de Ollama a descargar el modelo inmediatamente de los tensores de la GPU o la memoria RAM.
- **Beneficio**: El sistema recupera gigabytes de memoria instantáneamente para otras aplicaciones.

## 2. Parsing de JSON Robusto y Reparación Estructural

Los modelos locales a veces pueden generar respuestas malformadas debido a la cuantización o detenciones inesperadas. Orchestrator implementa un motor de extracción de JSON resiliente.

### Capacidades de Reparación
- **Trailing Commas**: Elimina automáticamente comas sobrantes al final de objetos o listas, que suelen romper el estándar JSON.
- **Balanceo de Estructuras**: Si una respuesta se corta antes de tiempo (truncamiento), el motor cuenta las llaves `{` y corchetes `[` abiertos y añade los cierres correspondientes `}` `]` para intentar salvar la mayor parte del mensaje.
- **Extracción Inteligente**: Busca patrones de bloques de código Markdown (```json) y, en su defecto, utiliza un algoritmo de búsqueda de primer y último delimitador.

## 3. Configuración del System Prompt

El "cerebro" del agente ha sido reforzado con instrucciones específicas para minimizar errores de formato:
- Obligatoriedad de formato JSON estricto.
- Prohibición de incluir caracteres de control innecesarios o comas finales.
