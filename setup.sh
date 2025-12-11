#!/bin/bash

# Instalar dependencias de Python
echo "Instalando dependencias..."
uv pip install -r requirements.txt

# Descargar modelos y ficheros necesarios para los plugins
echo "Descargando modelos..."
uv run agent.py download-files

echo "¡Configuración completada!"
