import discord
from discord.ext import commands
from discord import app_commands
class avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Get a user's avatar")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        await interaction.response.defer()
        if user is None:
            user = self.bot.get_user(interaction.user.id)
        embed = discord.Embed(title=f"{user.name}'s avatar", color=0x00ff00)
        embed.set_image(url=user.avatar)
        embed.timestamp = interaction.created_at
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(avatar(bot))
