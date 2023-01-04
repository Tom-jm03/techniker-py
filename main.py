import discord, asyncio, os, datetime, traceback
from typing import Literal, Optional
from dotenv import load_dotenv
from datetime import timedelta
from discord.ext import commands
from src.functions import load_extension, create_tables
load_dotenv()

global error_file
error_file = open("error.log", "w")
discord_token = os.getenv("DISCORD_TOKEN")
intents = discord.Intents(messages=True, guilds=True, members=True)
bot = discord.ext.commands.Bot(command_prefix="&", intents=intents)
exit = 0
bot.launch_time = datetime.datetime.now()
intents.members = True
intents.dm_messages = True
intents.messages = True
intents.message_content = True
intents.voice_states = True
intents.guilds = True
bot.synced = False

@bot.event
async def on_ready():
    print("Bot is ready ✅")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="&help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="Error", description="That command does not exist.", color=0xff0000)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Error", description="You do not have the permissions to use this command.", color=0xff0000)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Error", description="You are missing a required argument.", color=0xff0000)
        await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
@commands.guild_only()
async def uptime(ctx: commands.Context) -> None:
    async with ctx.channel.typing():
        delta_uptime = datetime.datetime.now() - bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    print("Syncing commands...")
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()
        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return
    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1
    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

async def main():
    try:
        await create_tables()
        await load_extension(bot)
        await bot.start(discord_token)
    except:
        tb = traceback.format_exc()
        now = datetime.datetime.now()
        print(f"Something went wrong while starting the bot ❌\n{tb}")
        error_file.write(f"{now}: {tb}")

asyncio.run(main())
