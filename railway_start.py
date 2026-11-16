import runpy
from pathlib import Path

from admin_profile_ui import install_admin_profile_ui
from anti_bot_registration_patch import patch_app_file as patch_anti_bot_approval
from anti_link_registration_patch import patch_app_file as patch_anti_link
from channel_nuke import patch_app_file as patch_nuke
from guild_profile_settings import install_guild_profile_settings
from profile_upload_support import install_profile_upload_support
import web_server
from web_server import start_website

ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "app.py"

if not APP_FILE.is_file():
    raise FileNotFoundError(f"No encontré el archivo del bot: {APP_FILE}")

# Install only idempotent registrations, without the legacy patch chain.
patch_nuke(APP_FILE)
patch_anti_bot_approval(APP_FILE)
patch_anti_link(APP_FILE)
install_guild_profile_settings(web_server.Handler)
install_profile_upload_support(web_server.Handler)
install_admin_profile_ui()
website_server = start_website()
if website_server is None:
    print("Aviso: no se inició la web; verifica que exista website/index.html.")

print("Iniciando Vantarmor Commands...")
runpy.run_path(str(APP_FILE), run_name="__main__")
