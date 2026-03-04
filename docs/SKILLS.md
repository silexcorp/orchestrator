# Habilidades (Skills)

Las habilidades son paquetes de instrucciones y contexto que proporcionan al agente experiencia especializada.

---

## Uso de Habilidades

1. Abre la ventana de gestión (**Ctrl + Shift + M**) → pestaña **Skills**.
2. Verás las habilidades disponibles en tu carpeta local.
3. Puedes importar nuevas habilidades haciendo clic en el botón **Import...** y seleccionando un archivo Markdown.

### Ubicación de archivos
Las habilidades se guardan como archivos `.md` en:
`~/.config/orchestrator/skills/`

---

## Creación de Habilidades

Puedes crear tus propias habilidades escribiendo un archivo Markdown con el siguiente formato sugerido:

```markdown
# [Nombre de la Habilidad]

Eres un experto en [campo específico]. 

## Metodología
1. Identifica el problema.
2. Aplica [técnica específica].
3. Formatea la respuesta como [formato deseado].
```

Una vez guardado en la carpeta de `skills/`, aparecerá automáticamente en Orchestrator.

---

## Selección Inteligente de Capacidades

Para ahorrar tokens, Orchestrator no envía todas las instrucciones de todas las habilidades en cada mensaje. Solo carga el contenido completo de las habilidades que el agente determine necesarias para la tarea actual según el contexto inicial.
