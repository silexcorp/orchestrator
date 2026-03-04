#!/bin/bash

# Script para construir el ejecutable de Orchestrator usando PyInstaller

# Activar entorno virtual
source venv/bin/activate

# Limpiar compilaciones anteriores
rm -rf build dist *.spec

# Ejecutar PyInstaller
# --onefile: Un solo archivo ejecutable
# --windowed: No abrir consola al ejecutar
# --add-data: Incluir directorios necesarios
# --noconfirm: No pedir confirmación para sobreescribir
pyinstaller --onefile --windowed \
    --name "Orchestrator" \
    --add-data "core:core" \
    --add-data "ui:ui" \
    --add-data "styles.py:." \
    --add-data "screenshot:screenshot" \
    main.py

echo "Construcción completada. El ejecutable se encuentra en la carpeta 'dist/'"
