import runpy
from pathlib import Path

from channel_nuke import patch_app_file
from web_server import start_website

ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "app.py"

if not APP_FILE.is_file():
    raise FileNotFoundError(f"No encontré el archivo del bot: {APP_FILE}")

# Install only the idempotent /nuke registration; no large patch pipeline.
patch_app_file(APP_FILE)

# Keep the website and Discord bot alive together in the same Railway service.
website_server = start_website()
if website_server is None:
    print("Aviso: no se inició la web; verifica que exista website/index.html.")

print("Iniciando Vantarmor Commands...")
runpy.run_path(str(APP_FILE), run_name="__main__")
