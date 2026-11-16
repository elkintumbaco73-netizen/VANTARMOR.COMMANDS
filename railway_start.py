import runpy
from pathlib import Path

from anti_bot_approval import patch_app_file as patch_anti_bot_approval
from channel_nuke import patch_app_file as patch_nuke
from web_server import start_website

ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "app.py"

if not APP_FILE.is_file():
    raise FileNotFoundError(f"No encontré el archivo del bot: {APP_FILE}")

patch_nuke(APP_FILE)
patch_anti_bot_approval(APP_FILE)
website_server = start_website()
if website_server is None:
    print("Aviso: no se inició la web; verifica que exista website/index.html.")

print("Iniciando Vantarmor Commands...")
runpy.run_path(str(APP_FILE), run_name="__main__")
