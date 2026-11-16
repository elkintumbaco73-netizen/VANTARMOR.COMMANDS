"""Premium slash command to safely recreate a text channel without its messages."""
from typing import Optional

import discord
from discord import app_commands


class NukeConfirmView(discord.ui.View):
    def __init__(self, requester_id: int, channel: discord.TextChannel):
        super().__init__(timeout=60)
        self.requester_id = requester_id
        self.channel = channel

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.requester_id:
            await interaction.response.send_message("Solo quien inició el comando puede confirmar esta acción.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirmar recreación", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None or self.channel.guild.id != guild.id:
            await interaction.response.send_message("El servidor ya no está disponible.", ephemeral=True)
            return
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("Necesitas Administrar canales para confirmar.", ephemeral=True)
            return
        bot_member = guild.me
        if bot_member is None or not bot_member.guild_permissions.manage_channels:
            await interaction.response.send_message("Al bot le falta el permiso Administrar canales.", ephemeral=True)
            return

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="Recreando el canal…", view=self)
        original = self.channel
        replacement = None
        try:
            replacement = await original.clone(reason=f"/nuke confirmado por {interaction.user} ({interaction.user.id})")
            await replacement.edit(position=original.position, reason="Restaurar la posición del canal recreado")
            await original.delete(reason=f"Canal recreado por /nuke de {interaction.user} ({interaction.user.id})")
        except (discord.Forbidden, discord.HTTPException) as error:
            if replacement is not None:
                try:
                    await replacement.delete(reason="Limpieza tras fallo de /nuke; se conservó el canal original")
                except (discord.Forbidden, discord.HTTPException):
                    await interaction.followup.send("Falló la recreación; el original se conserva. Revisa manualmente el canal duplicado.", ephemeral=True)
                    return
            await interaction.followup.send("No se pudo recrear el canal; el original se conserva. Revisa el permiso Administrar canales.", ephemeral=True)
            return
        await interaction.followup.send(f"✅ Canal recreado: {replacement.mention}. Los mensajes no se copian.", ephemeral=True)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="Acción cancelada; no se modificó ningún canal.", view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


async def nuke_command(interaction: discord.Interaction, canal: Optional[discord.TextChannel] = None):
    # Import lazily: railway_start.py applies compatibility fixes before app.py
    # imports premium_security_system, so Optional is defined before decorators run.
    from premium_security_system import _require_premium_admin

    if not await _require_premium_admin(interaction):
        return
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("Necesitas el permiso Administrar canales.", ephemeral=True)
        return
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("Este comando solo funciona dentro de un servidor.", ephemeral=True)
        return
    target = canal or interaction.channel
    if not isinstance(target, discord.TextChannel) or target.guild.id != guild.id:
        await interaction.response.send_message("Selecciona un canal de texto del mismo servidor.", ephemeral=True)
        return
    bot_member = guild.me
    if bot_member is None or not bot_member.guild_permissions.manage_channels:
        await interaction.response.send_message("Al bot le falta el permiso Administrar canales.", ephemeral=True)
        return
    if getattr(guild, "rules_channel", None) == target:
        await interaction.response.send_message("No se puede recrear el canal de reglas con este comando.", ephemeral=True)
        return
    await interaction.response.send_message(
        f"⚠️ Esto eliminará **#{target.name}** y creará un clon vacío. Los mensajes no se copian. Confirma para continuar.",
        view=NukeConfirmView(interaction.user.id, target), ephemeral=True,
    )


def register_channel_nuke(tree):
    if tree.get_command("nuke") is None:
        tree.command(name="nuke", description="Recrea un canal de texto sin copiar sus mensajes")(nuke_command)


def patch_app_file(app_file):
    source = app_file.read_text(encoding="utf-8")
    import_anchor = "from discord import app_commands\n"
    import_line = "from channel_nuke import register_channel_nuke\n"
    tree_line = "tree = app_commands.CommandTree(client)\n"
    register_line = "register_channel_nuke(tree)\n"
    if import_line not in source:
        if import_anchor not in source:
            raise RuntimeError("No encontré el import de app_commands para registrar /nuke.")
        source = source.replace(import_anchor, import_anchor + import_line, 1)
    if register_line not in source:
        if tree_line not in source:
            raise RuntimeError("No encontré la creación del árbol de comandos para registrar /nuke.")
        source = source.replace(tree_line, tree_line + register_line, 1)
    app_file.write_text(source, encoding="utf-8")


__all__ = ["patch_app_file", "register_channel_nuke"]
