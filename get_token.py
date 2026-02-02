import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Mismos scopes que el original
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

def generar_token():
    if not os.path.exists('credentials.json'):
        print("❌ Error: No se encuentra credentials.json")
        return

    print("🚀 Iniciando flujo de autenticación...")
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    
    # Esto FORZARÁ la apertura del navegador
    creds = flow.run_local_server(port=0)
    
    # Guardamos el archivo que Claude necesita
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("✅ ¡ÉXITO! Se ha creado el archivo token.json")
    print("Ahora puedes cerrar esta ventana y usar Claude Desktop.")

if __name__ == "__main__":
    generar_token()