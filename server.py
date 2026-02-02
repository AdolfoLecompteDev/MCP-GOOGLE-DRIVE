import os
import sys
from fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- CONFIGURACIÓN DE RUTAS ---
# Esto asegura que el script busque el token y las credenciales en su propia carpeta
os.chdir(os.path.dirname(os.path.abspath(__file__)))

SCOPES = [
    'https://www.googleapis.com/auth/drive', 
    'https://www.googleapis.com/auth/spreadsheets'
]
CLIENT_SECRET_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

mcp = FastMCP("google-mcp-personal")

def get_services():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(f"Falta {CLIENT_SECRET_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    drive = build('drive', 'v3', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)
    return drive, sheets

# --- HERRAMIENTAS DE DRIVE ---

@mcp.tool()
def listar_archivos(folder_id: str = None) -> str:
    """Lista archivos de tu Drive personal."""
    drive, _ = get_services()
    query = f"'{folder_id or 'root'}' in parents and trashed=false"
    results = drive.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return "\n".join([f"- {f['name']} ({f['id']})" for f in files]) or "Carpeta vacía."

@mcp.tool()
def subir_archivo_a_drive(ruta_local: str, folder_id: str = None) -> str:
    """Sube un archivo de tu PC a Google Drive."""
    drive, _ = get_services()
    name = os.path.basename(ruta_local)
    metadata = {'name': name}
    if folder_id: metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(ruta_local, resumable=True)
    file = drive.files().create(body=metadata, media_body=media, fields='id').execute()
    return f"Archivo subido con éxito. ID: {file.get('id')}"

# --- HERRAMIENTAS DE SHEETS ---

@mcp.tool()
def crear_google_sheet(titulo: str) -> str:
    """Crea una nueva hoja de cálculo de Google."""
    _, sheets = get_services()
    spreadsheet = {'properties': {'title': titulo}}
    res = sheets.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
    return f"Sheet creada: https://docs.google.com/spreadsheets/d/{res.get('spreadsheetId')}"

@mcp.tool()
def escribir_en_sheet(sheet_id: str, rango: str, valores: list):
    """Escribe datos en una Sheet. Ejemplo: valores=[['Nombre', 'Edad'], ['Adolfo', 25]]"""
    _, sheets = get_services()
    body = {'values': valores}
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=rango,
        valueInputOption="RAW", body=body).execute()
    return "Datos escritos correctamente."

# --- HERRAMIENTAS DEL SISTEMA (LOCAL) ---

@mcp.tool()
def leer_archivo_local(ruta: str) -> str:
    """Lee el contenido de un archivo en tu PC."""
    with open(ruta, 'r', encoding='utf-8') as f:
        return f.read()

@mcp.tool()
def listar_directorio_local(ruta: str) -> list:
    """Lista los archivos de una carpeta de tu PC."""
    return os.listdir(ruta)
# --- MÁS HERRAMIENTAS DE DRIVE ---

@mcp.tool()
def crear_carpeta_drive(nombre: str, parent_id: str = None) -> str:
    """Crea una nueva carpeta en Drive."""
    drive, _ = get_services()
    metadata = {
        'name': nombre,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]
        
    file = drive.files().create(body=metadata, fields='id').execute()
    return f"Carpeta '{nombre}' creada con éxito. ID: {file.get('id')}"

@mcp.tool()
def borrar_archivo_drive(file_id: str) -> str:
    """Mueve un archivo o carpeta de Drive a la papelera."""
    drive, _ = get_services()
    drive.files().update(fileId=file_id, body={'trashed': True}).execute()
    return f"El archivo con ID {file_id} ha sido movido a la papelera."

@mcp.tool()
def descargar_archivo_drive(file_id: str, ruta_destino: str) -> str:
    """Descarga un archivo de Drive a una ruta específica de tu PC."""
    import io
    from googleapiclient.http import MediaIoBaseDownload
    
    drive, _ = get_services()
    request = drive.files().get_media(fileId=file_id)
    fh = io.FileIO(ruta_destino, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return f"Archivo descargado con éxito en: {ruta_destino}"

if __name__ == "__main__":
    mcp.run()