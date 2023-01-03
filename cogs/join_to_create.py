from discord.ext import commands
from discord import app_commands, Permissions
from src.buttons import Confirm
import discord, aiosqlite, datetime

class join_to_create(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="jtc", description="Commands for managing join to create channels", default_permissions=Permissions(manage_channels=True))

    @group.command(name="create", description="Create a channel when a user joins a specified voice channel")
    async def create(self, interaction: discord.Interaction, channel_name: str, channel_size: int = 5, channel_bits: int = 64):
        async with aiosqlite.connect("techniker.db") as db:
            await interaction.response.defer()
            guild = self.bot.get_guild(interaction.guild.id)
            channel = await guild.create_voice_channel(channel_name, user_limit=channel_size, bitrate=(channel_bits*1000))
            await db.execute("INSERT INTO join_to_create VALUES (?, ?, ?, ?, ?, ?, ?)", (interaction.guild.id, channel.id, channel_size, interaction.user.id, channel_bits, datetime.datetime.now(), interaction.user.id))
            await db.commit()
        await interaction.followup.send(f"Created a join to create channel for {channel_name} ✅")

    @group.command(name="delete", description="Delete a join to create channel")
    async def delete(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        async with aiosqlite.connect("techniker.db") as db:
            await interaction.response.defer(ephemeral=True)
            c = await db.cursor()
            await c.execute("SELECT * FROM join_to_create WHERE channel_id = ?", (channel.id, ))
            result = await c.fetchone()
            if result != None:
                view = Confirm()
                embed = discord.Embed(title=f"Are you sure you want to delete this join to create channel? This also includes already created user-channels.", description=f"Channel: {channel.mention}", color=0xff0000)
                await interaction.followup.send(embed=embed, view=view) 
                await view.wait()
                if view.value:
                    await channel.delete()
                    await c.execute("SELECT join_to_create_channel_id FROM join_to_create_users WHERE channel_id = ?", (channel.id, ))
                    await db.execute("DELETE FROM join_to_create WHERE channel_id = ?", (channel.id,))
                    result2 = await c.fetchall()
                    if result2 != None:
                        for i in result2:
                            channel = self.bot.get_channel(i[0])
                            await channel.delete()
                    await db.commit()
                    await c.close()
            else:
                embed = discord.Embed(title=f"Error.", description="This channel is not a join to create channel.❌", color=0xff0000)
                await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel and after.channel is not None:
            async with aiosqlite.connect("techniker.db") as db:
                c = await db.cursor()
                await c.execute("SELECT * FROM join_to_create WHERE channel_id = ?", (after.channel.id, ))
                result1 = await c.fetchone()
                if result1 == None:
                    return
                if result1 != None:
                    category = after.channel.category
                    await c.execute("SELECT join_to_create_channel_id FROM join_to_create_users WHERE user_id = ? AND guild_id = ? AND channel_id = ?", (member.id, member.guild.id, result1[1], ))
                    result2 = await c.fetchone()
                    if result2 == None:
                        new_channel = await member.guild.create_voice_channel(name=f"{member.nick}'s Channel", user_limit=result1[2], bitrate=(result1[4]*1000), category=category)
                        await new_channel.set_permissions(member, connect=True, speak=True, )
                        await member.move_to(new_channel)
                        await c.execute("INSERT INTO join_to_create_users VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING", (member.guild.id, member.id, result1[1], new_channel.id, datetime.datetime.now(), ))
                        await db.commit()
                        await c.close()
                        if new_channel.members == []:
                            await new_channel.delete()
                    if result2 != None:
                        await c.execute("SELECT join_to_create_channel_id FROM join_to_create_users WHERE user_id = ? AND guild_id = ? AND channel_id = ?", (member.id, member.guild.id, result1[1], ))
                        result2 = await c.fetchone()
                        channel = self.bot.get_channel(result2[0])
                        await member.move_to(channel)
                        await c.close()

    @commands.Cog.listener("on_voice_state_update")
    async def delete_channel_after_leave(self, member, before, after):
        if before.channel != after.channel and before.channel is not None:
            async with aiosqlite.connect("techniker.db") as db:
                c = await db.cursor()
                await c.execute("SELECT * FROM join_to_create_users WHERE join_to_create_channel_id = ?", (before.channel.id, ))
                result = await c.fetchone()
                if result != None:
                    if after.channel == None and before.channel.id == result[3] and before.channel.id != result[2]:
                        if before.channel.members == []:
                            await before.channel.delete()
                        await before.channel.delete()
                    elif before.channel.id == result[3] and before.channel.id != result[2] and after.channel.id != result[2]:
                        if before.channel.members == []:
                            await before.channel.delete()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        async with aiosqlite.connect("techniker.db") as db:
            await db.execute("DELETE FROM join_to_create WHERE channel_id = ?", (channel.id,))
            await db.execute("DELETE FROM join_to_create_users WHERE join_to_create_channel_id = ?", (channel.id,))
            await db.commit()

async def setup(bot):
    await bot.add_cog(join_to_create(bot))
