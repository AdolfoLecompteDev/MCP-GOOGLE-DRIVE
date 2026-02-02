# Google Drive & Sheets MCP Server

Este servidor permite que Claude Desktop gestione tu Google Drive y Sheets directamente usando el protocolo MCP.

## Funcionalidades
- 📂 **Drive:** Listar, subir, descargar y crear carpetas.
- 📊 **Sheets:** Crear hojas de cálculo y escribir datos.
- 💻 **Sistema:** Leer archivos locales para procesarlos.

## Configuración
1. Obtén tu `credentials.json` desde Google Cloud Console (OAuth Desktop App).
2. Instala dependencias: `pip install -r requirements.txt`.
3. Ejecuta `server.py` manualmente la primera vez para generar el `token.json`.
