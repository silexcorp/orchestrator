# Guía de Construcción y Empaquetado

Esta guía explica cómo generar la versión distribuible (ejecutable) de Orchestrator para sistemas Linux.

## Generación del Ejecutable

Orchestrator utiliza [PyInstaller](https://pyinstaller.org/) para convertir el código fuente de Python en un binario independiente que incluye todas las dependencias necesarias (incluyendo PyQt6).

### Requisitos Previos

Asegúrate de tener el entorno virtual configurado e instalado:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
```

### Script de Construcción

El proyecto incluye un script de bash llamado `build_executable.sh` que automatiza el proceso con las configuraciones óptimas.

**Lo que hace el script:**
1. Activa el entorno virtual.
2. Limpia carpetas de compilación previas (`build/`, `dist/`).
3. Ejecuta PyInstaller con las siguientes banderas:
   - `--onefile`: Genera un único binario comprimido.
   - `--windowed`: La aplicación no abrirá una terminal persistente al iniciarse.
   - `--add-data`: Incluye las carpetas `core`, `ui`, `screenshot` y el archivo `styles.py` dentro del paquete.

### Ejecución del Script

Desde la raíz del proyecto, ejecuta:

```bash
./build_executable.sh
```

El resultado será un archivo llamado `Orchestrator` dentro del directorio `dist/`.

## Distribución

El archivo generado en `dist/Orchestrator` es un binario ELF de 64 bits autocontenido. Puedes copiar este archivo a cualquier otra máquina Linux (con arquitectura compatible) y ejecutarlo sin necesidad de instalar Python o las dependencias manualmente.

> [!NOTE]
> Para que el editor funcione correctamente, el usuario debe tener **Ollama** instalado y configurado en su sistema, ya que el ejecutable se comunica con el servicio local de Ollama.
