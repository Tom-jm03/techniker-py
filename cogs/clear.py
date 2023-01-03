import discord, asyncio
from discord import app_commands
from discord.ext import commands

class clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.command(name="clear", description="Clears messages in a channel")
    async def clear(self, interaction, amount: int = 1):
        await interaction.response.defer()
        purger = await interaction.channel.purge(limit=amount, before=interaction.created_at)
        embed = discord.Embed(title="Cleared messages", description=f"Deleted {len(purger)} messages.", color=0x00ff00)
        message = await interaction.followup.send(embed=embed)
        await asyncio.sleep(2)
        await message.delete()

async def setup(bot):
    await bot.add_cog(clear(bot))
