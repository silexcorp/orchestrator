#!/bin/bash

# Script para construir el ejecutable de Orchestrator usando PyInstaller

# Activar entorno virtual
source venv/bin/activate

# Limpiar compilaciones anteriores
rm -rf build dist *.spec

# Ejecutar PyInstaller
# --onefile: Un solo archivo ejecutable
# --windowed: No abrir consola al ejecutar
# --add-data: Incluir solo recursos NO-Python (imágenes, etc.)
# --collect-all: Asegura que se incluyan dependencias complejas si es necesario
# --noconfirm: No pedir confirmación para sobreescribir
source venv/bin/activate && \
rm -rf build dist Orchestrator *.spec && \
pyinstaller --onefile \
    --name "Orchestrator" \
    --paths "." \
    --add-data "ui:ui" \
    --add-data "core:core" \
    --add-data "styles.py:." \
    --collect-all "pymdownx" \
    --collect-all "markdown" \
    --noconfirm \
    main.py && \
cp dist/Orchestrator ./Orchestrator

echo "Construcción completada. El ejecutable se encuentra en la carpeta 'dist/'"
