import runpy
from pathlib import Path

from anti_link_registration_patch import patch_app_file as patch_anti_link

ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "app.py"

if not APP_FILE.is_file():
    raise FileNotFoundError(f"No encontré el archivo del bot: {APP_FILE}")

# Install idempotently; link filtering dispatches through the existing on_message event.
patch_anti_link(APP_FILE)
print("Iniciando Vantarmor Commands...")
runpy.run_path(str(APP_FILE), run_name="__main__")
