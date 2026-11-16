"""Idempotently register the anti-link listener and slash command."""
from pathlib import Path


def patch_app_file(app_file: Path) -> None:
    source = app_file.read_text(encoding="utf-8")
    import_anchor = "from discord import app_commands\n"
    import_line = "from anti_link_protection import register_anti_link\n"
    tree_anchor = "tree = app_commands.CommandTree(client)\n"
    register_line = "register_anti_link(tree, client, GUILD_ID)\n"
    if import_line not in source:
        if import_anchor not in source:
            raise RuntimeError("No encontré el import app_commands para instalar /anti-link.")
        source = source.replace(import_anchor, import_anchor + import_line, 1)
    if register_line not in source:
        if tree_anchor not in source:
            raise RuntimeError("No encontré el árbol de comandos para instalar /anti-link.")
        source = source.replace(tree_anchor, tree_anchor + register_line, 1)
    app_file.write_text(source, encoding="utf-8")
