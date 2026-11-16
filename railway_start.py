import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "app.py"

if not APP_FILE.is_file():
    raise FileNotFoundError(f"No encontré el archivo del bot: {APP_FILE}")

print("Iniciando Vantarmor Commands (versión limpia)...")
runpy.run_path(str(APP_FILE), run_name="__main__")
