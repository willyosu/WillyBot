import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# bot.py
# - Main file where the bot is run using a commands.Bot instance

load_dotenv()
bot = commands.Bot(command_prefix=['~', '😠'], owner_id = int(os.environ.get("BOT_OWNER_ID")), intents=discord.Intents.all())

@bot.event
async def on_ready():
	await load_all()
	print("Bot is up and running!")
	await bot.change_presence(status=discord.Status.online, activity=discord.Game("~profile"))

async def load_all():
	for file in os.listdir('./cogs'):
		if file.endswith('.py'):
			await bot.load_extension(f'cogs.{file[:-3]}')

async def unload_all():
	for file in os.listdir('./cogs'):
		if file.endswith('.py'):
			await bot.unload_extension(f'cogs.{file[:-3]}')

@bot.command(description="Load a cog into the bot.")
@commands.is_owner()
async def load(context, extension: str) -> None:
	await bot.load_extension(f'cogs.{extension}')
	await context.send(f'Loaded cog: `{extension}`')

@bot.command(description="Unload a cog from the bot.")
@commands.is_owner()
async def unload(context, extension: str) -> None:
	await bot.unload_extension(f'cogs.{extension}')
	await context.send(f'Unloaded cog: `{extension}`')

@bot.command(description="Reload a cog into the bot.")
@commands.is_owner()
async def reload(context, extension: str) -> None:
	try:
		await bot.unload_extension(f'cogs.{extension}')
	except:
		pass
	await bot.load_extension(f'cogs.{extension}')
	await context.send(f'Reloaded cog: `{extension}`')

@bot.command(description="Reload a cog into the bot.")
@commands.is_owner()
async def reloadall(context) -> None:
	try:
		await unload_all()
		await load_all()
	except:
		pass
	await context.send(f'`Reloaded all cogs.`')

bot.run(os.environ.get("BOT_TOKEN"), root_logger=True)