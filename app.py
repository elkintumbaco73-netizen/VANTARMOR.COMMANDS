@@
 spam_records = {}
 number_game_lock = asyncio.Lock()
+active_giveaways = {}
+
+
+async def _server_join_url(guild: discord.Guild) -> str:
+    try:
+        invites = await guild.invites()
+        for invite in invites:
+            if invite.url and not invite.revoked and invite.max_age == 0:
+                return invite.url
+    except (discord.Forbidden, discord.HTTPException):
+        pass
+    if getattr(guild, "vanity_url_code", None):
+        return f"https://discord.gg/{guild.vanity_url_code}"
+    return f"https://discord.com/channels/{guild.id}"
+
+
+async def _finalize_giveaway(guild_id: int):
+    giveaway = active_giveaways.pop(guild_id, None)
+    if not giveaway:
+        return
+
+    guild = client.get_guild(guild_id)
+    if guild is None:
+        return
+
+    channel = client.get_channel(giveaway["channel_id"])
+    if channel is None:
+        return
+
+    entries = list(giveaway["entries"])
+    winners = random.sample(entries, k=min(giveaway["winners_count"], len(entries))) if entries else []
+
+    winners_text = ", ".join(f"<@{winner}>" for winner in winners) if winners else "No hubo participantes."
+    result_embed = discord.Embed(
+        title="✅ Sorteo finalizado",
+        description=f"El sorteo de **{giveaway['prize']}** ha terminado.",
+        color=discord.Color.green(),
+    )
+    result_embed.add_field(name="Premio", value=giveaway["prize"], inline=False)
+    result_embed.add_field(name="Ganadores", value=winners_text, inline=False)
+    result_embed.set_footer(text=f"Ganadores: {len(winners)} | Finalizado")
+    await channel.send(embed=result_embed)
+
+    if not winners:
+        return
+
+    join_url = await _server_join_url(guild)
+    for winner_id in winners:
+        try:
+            member = guild.get_member(winner_id) or await guild.fetch_member(winner_id)
+            view = discord.ui.View(timeout=180)
+            view.add_item(discord.ui.Button(label="Entrar al servidor", url=join_url, emoji="🚀"))
+            dm_embed = discord.Embed(
+                title="🎉 Has ganado un sorteo",
+                description=f"Felicidades, has sido elegido como ganador del premio **{giveaway['prize']}** en **{guild.name}**.",
+                color=discord.Color.gold(),
+            )
+            dm_embed.add_field(name="Premio", value=giveaway["prize"], inline=False)
+            dm_embed.add_field(name="Servidor", value=guild.name, inline=False)
+            dm_embed.add_field(name="Ganadores", value=f"<@{winner_id}>", inline=False)
+            await member.send(embed=dm_embed, view=view)
+        except (discord.Forbidden, discord.HTTPException):
+            try:
+                await channel.send(f"No pude enviar el DM a <@{winner_id}>, pero sigue siendo ganador del sorteo.", allowed_mentions=discord.AllowedMentions.none())
+            except (discord.Forbidden, discord.HTTPException):
+                pass
+
+
+class GiveawayJoinView(discord.ui.View):
+    def __init__(self, guild_id: int, giveaway_id: str):
+        super().__init__(timeout=None)
+        self.guild_id = guild_id
+        self.giveaway_id = giveaway_id
+
+    @discord.ui.button(label="🎁 Participar", style=discord.ButtonStyle.primary, custom_id="giveaway:join")
+    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
+        giveaway = active_giveaways.get(self.guild_id)
+        if not giveaway or giveaway["id"] != self.giveaway_id:
+            await interaction.response.send_message("Este sorteo ya terminó o no existe.", ephemeral=True)
+            return
+        if interaction.user.id in giveaway["entries"]:
+            await interaction.response.send_message("Ya estás participando en este sorteo.", ephemeral=True)
+            return
+        giveaway["entries"].add(interaction.user.id)
+        await interaction.response.send_message(f"✅ {interaction.user.mention} ya participa en el sorteo de **{giveaway['prize']}**.", ephemeral=True)
+
+
+async def _start_giveaway_timer(guild_id: int, seconds: int):
+    await asyncio.sleep(seconds)
+    await _finalize_giveaway(guild_id)
@@
 @tree.command(name="sorteo", description="Crea un sorteo en este canal", guild=GUILD)
 @app_commands.describe(ganadores="Ganadores (1 a 10)", duracion="10m, 2h, 3d", premio="Premio opcional")
 async def giveaway(interaction, ganadores: app_commands.Range[int, 1, 10], duracion: str, premio: Optional[str] = None):
     seconds = duration_seconds(duracion)
     if seconds is None:
         await interaction.response.send_message("Duración no válida. Usa `10m`, `2h` o `3d`.", ephemeral=True)
         return
-    await interaction.response.send_message("El comando de sorteo requiere la versión anterior del módulo; vuelve a intentarlo después.", ephemeral=True)
+    if interaction.guild_id in active_giveaways:
+        await interaction.response.send_message("Ya hay un sorteo activo en este servidor. Finalízalo antes de crear otro.", ephemeral=True)
+        return
+
+    prize = (premio or "Premio sorpresa").strip()
+    if not prize:
+        await interaction.response.send_message("Escribe un premio válido.", ephemeral=True)
+        return
+
+    if interaction.channel is None:
+        await interaction.response.send_message("Este comando solo funciona en un canal del servidor.", ephemeral=True)
+        return
+
+    giveaway_id = f"giveaway-{interaction.guild_id}-{int(time.time())}"
+    active_giveaways[interaction.guild_id] = {
+        "id": giveaway_id,
+        "guild_id": interaction.guild_id,
+        "channel_id": interaction.channel.id,
+        "prize": prize,
+        "winners_count": int(ganadores),
+        "entries": set(),
+        "created_by": interaction.user.id,
+        "ends_at": time.time() + seconds,
+    }
+
+    embed = discord.Embed(
+        title="🎉 Sorteo activo",
+        description=f"Participa para ganar **{prize}**.",
+        color=discord.Color.gold(),
+    )
+    embed.add_field(name="Premio", value=prize, inline=False)
+    embed.add_field(name="Ganadores", value=str(ganadores), inline=True)
+    embed.add_field(name="Finaliza", value=f"<t:{int(time.time() + seconds)}:f>", inline=True)
+    embed.set_footer(text="Pulsa el botón para participar.")
+
+    await interaction.response.send_message("✅ Sorteo creado correctamente.", ephemeral=True)
+    message = await interaction.channel.send(embed=embed, view=GiveawayJoinView(interaction.guild_id, giveaway_id))
+    active_giveaways[interaction.guild_id]["message_id"] = message.id
+    asyncio.create_task(_start_giveaway_timer(interaction.guild_id, seconds))
@@
 @tree.command(name="cookie", description="Juego de tocar la galleta", guild=GUILD)
 async def cookie(interaction):
     await interaction.response.send_message("🍪 Juego de galleta disponible después del redeploy.")
