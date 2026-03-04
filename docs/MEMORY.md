# Sistema de Memoria de Orchestrator

La versión Python de Orchestrator utiliza un sistema de memoria simplificado pero eficaz para proporcionar contexto a largo plazo.

## Capas de Memoria

### 1. Perfil de Usuario (`user_profiles.json`)
Contiene resúmenes destilados de quién es el usuario y sus preferencias generales según lo aprendido por cada agente.

### 2. Memoria de Trabajo (`memory_entries.json`)
Entradas individuales extraídas de conversaciones pasadas que contienen hechos o datos específicos.

## Funcionamiento Técnico

### Extracción
Cuando una conversación finaliza o alcanza un punto de guardado, el agente analiza el historial y extrae nuevos conocimientos que se guardan como `MemoryEntry`.

### Búsqueda (BM25)
A diferencia de la versión macOS que utiliza búsqueda vectorial (Embeddings), la versión Linux actual utiliza un algoritmo de búsqueda por palabras clave **BM25**. 

Cuando realizas una pregunta, Orchestrator:
1. Divide tu consulta en tokens.
2. Busca en la base de datos de memoria las entradas con mayor coincidencia de términos.
3. Inyecta los resultados más relevantes en el prompt de sistema del agente.

## Gestión de Datos
Puedes ver y gestionar la memoria acumulada desde la pestaña **Memory** en la ventana de gestión de la aplicación.
