@@
 CONFIG_DEFAULTS = {
-    "ticket_role": {}, "ticket_category": {}, "ticket_log": {}, "audit_log": {},
+    "ticket_role": {}, "ticket_category": {}, "ticket_panel": {}, "ticket_log": {}, "audit_log": {},
     "autorole": {}, "blocked_words": {}, "antispam": {}, "antilink": {},
 }
@@
 @tree.command(name="ayuda", description="Muestra comandos disponibles", guild=GUILD)
 async def ayuda(interaction):
-    await interaction.response.send_message("Tickets: `/ticket-panel`, `/ticket-rol`, `/ticket-categoria`, `/ticket-rol-elimimar`, `/setlog-tickets`, `/unsetlog-tickets`. Seguridad: `/antispam`, `/antilink`, `/setlog`, `/unsetlog`. Moderación: `/time out usuario duracion`.", ephemeral=True)
+    await interaction.response.send_message("Tickets: `/ticket-panel`, `/ticket-rol`, `/ticket-categoria`, `/ticket-rol-eliminar`, `/setlog-tickets`, `/unsetlog-tickets`. Seguridad: `/antispam`, `/antilink`, `/setlog`, `/unsetlog`. Moderación: `/time out usuario duracion`.", ephemeral=True)
@@
-@tree.command(name="ticket-rol-elimimar", description="Quita el rol de soporte de tickets", guild=GUILD)
+@tree.command(name="ticket-rol-eliminar", description="Quita el rol de soporte de tickets", guild=GUILD)
 @app_commands.default_permissions(manage_guild=True)
 @app_commands.describe(rol="Rol de soporte que quieres eliminar de la configuración")
 async def ticket_role_remove_command(interaction: discord.Interaction, rol: discord.Role):
