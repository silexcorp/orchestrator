# Estética Antigravity (Premium Google Style)

Orchestrator utiliza la identidad visual de **Antigravity**, diseñada para transmitir innovación, potencia y claridad.

## Paleta de Colores

- **Fondo Principal (Deep Space)**: `#05060a` - Un azul-negro profundo que reduce la fatiga visual.
- **Acento Primario (Electric Cyan)**: `#00f2ff` - Usado para estados de enfoque, indicadores de actividad y llamadas a la acción.
- **Acento Secundario (Galactic Purple)**: `#8a2be2` - Usado para identificar "Pensamientos Neurales" y estados de usuario.
- **Gradientes**: Botón de envío con gradiente lineal de Cian a Púrpura, representando la fusión de lógica y creatividad.

## Componentes UI Clave

### 1. Glowing Capsule Input
El área de entrada de texto no es un simple cuadro de texto; es una cápsula diseñada con un borde reactivo que aumenta su brillo (glow cian) cuando el usuario interactúa con ella.

### 2. Neural Activity Log
Ubicado en la parte inferior derecha, este panel proporciona una ventana directa al proceso cognitivo del agente. Los logs están categorizados por colores:
- **Púrpura**: Pensamientos del modelo.
- **Cian**: Acciones del sistema (Tools).
- **Verde**: Observaciones y datos de sensores.
- **Rojo**: Errores críticos.

### 3. Responsive Chat Layout
El chat se adapta dinámicamente al ancho disponible en el panel derecho. Las burbujas de mensaje aprovechan el espacio horizontal para maximizar la legibilidad del código y las explicaciones extensas.

## Implementación Técnica

Los estilos están centralizados en `styles.py` y aplicados dinámicamente mediante hojas de estilo de Qt (QSS). Se utilizan transparencias (alfa) y bordes redondeados (14px - 28px) para mantener una estética suave y moderna.
