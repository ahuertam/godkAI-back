#!/bin/bash

# Instalar dependencias de Python
# Las dependencias viven en pyproject.toml + uv.lock. `package = false` en
# [tool.uv] evita que uv intente construir el proyecto (agent.py es un
# script, no un paquete instalable).
echo "Instalando dependencias..."
uv sync

# Descargar modelos y ficheros necesarios para los plugins
echo "Descargando modelos..."
uv run agent.py download-files

echo "¡Configuración completada!"
