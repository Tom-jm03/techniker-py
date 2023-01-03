import discord



class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title=f"Success.", description="This Join-To-Create Channel and all existing child-Channels have been deleted.", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.value = True
        self.stop()
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title=f"Cancelled.", description="This Join-To-Create Channel has not been deleted.", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.value = False
        self.stop()
