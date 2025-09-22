from discord.ext import commands
from discord import Status, Game, HTTPException
from core.database import Connection
import os

# cogs/server.py
# - (Roles) helper class for server role-specific ids
# - (Server) commands.Cog for server and moderation related commands/listeners

class Roles:

	MOD = 759476878523236403
	ADMIN = 105048534998388736

	COLORS = {
		"peach": 199890831027470338,
		"very red": 1200643221722763294,
		"red": 162264277888008193,
		"dark red": 162280539263467531,
		"poo brown": 338174388866383874,
		"orange": 162278465737850880,
		"dark orange": 1200643826126168115,
		"yellow": 162278656977141761,
		"very green": 273533854709579777,
		"green": 162281118626742283,
		"dark green": 162279043541106688,
		"teal": 271794668033802240,
		"very blue": 1200643369471332392,
		"lighter blue": 284479508763901952,
		"light blue": 162282900669202433,
		"blue": 162279350220226560,
		"dark blue": 162282183082508288,
		"lavender": 336393327777939457,
		"purple": 583733444325146626,
		"dark purple": 162279642970062849,
		"hot pink": 162280235142742017,
		"light pink": 162283570545557505,
		"pink": 335936596509458433,
		"invisible": 251903540795146251,
		"gray": 178132261089181696,
		"white": 207542152396406785,
		"black": 793587791644459019
	}
	NOTIFYS = {
		"videos": 746326444023742465,
		"streams": 746326084483547216,
		"quests": 915359756300996648,
		"minecraft": 1343357931034251345,
		"willybot": 1200643238009253948
	}

class Server(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot
		self.database = Connection()
		self.database.start()

	@commands.command(aliases=['color'], description="Change your color role.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def colorme(self, context, *, color: str = None) -> None:
		try:
			colors = Roles.COLORS.keys()
			ids = Roles.COLORS.values()
			color = color.lower().strip()
			
			if color in colors:
				# Remove all color roles from roles list, and append the desired color
				roles = [role for role in context.author.roles if role.id not in ids]
				roles.append(context.guild.get_role(Roles.COLORS.get(color)))
				await context.author.edit(roles=roles)
				await context.reply(f"Successfully changed color to **{color}**!", mention_author=False)
			else:
				raise
		except:
			await context.reply("Could not find that color! Here's a list of available colors:\n" + ", ".join(colors), mention_author=False)
	
	@commands.command(aliases=['uncolor'], description="Remove your color role.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def uncolorme(self, context) -> None:
		ids = Roles.COLORS.values()
		roles = [role for role in context.author.roles if role.id not in ids]
		await context.author.edit(roles=roles)
		await context.reply(f"Successfully removed all color roles!", mention_author=False)
	
	@commands.command(aliases=['notify'], description="Add a notify role.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def notifyme(self, context, *, notify: str) -> None:
		notifys = Roles.NOTIFYS.keys()
		notify = notify.lower().strip()
		if notify in notifys:
			roles = set(context.author.roles)
			roles.add(context.guild.get_role(Roles.NOTIFYS.get(notify)))
			await context.author.edit(roles=roles)
			await context.reply(f"Successfully turned on notifications for **{notify}**!", mention_author=False)
		else:
			await context.reply("Could not find that role! Here's a list of available notifys:\n" + ", ".join(notifys), mention_author=False)
	
	@commands.command(aliases=['unnotify'], description="Remove a notify role.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def unnotifyme(self, context, *, notify: str) -> None:
		notifys = Roles.NOTIFYS.keys()
		notify = notify.lower().strip()
		if notify in notifys:
			roles = [role for role in context.author.roles if role.id != Roles.NOTIFYS.get(notify)]
			await context.author.edit(roles=roles)
			await context.reply(f"Successfully turned off notifications for **{notify}**!", mention_author=False)
		else:
			await context.reply("Could not find that role! Here's a list of available notifys:\n" + ", ".join(notifys), mention_author=False)
		
	# Moderator and Admin commands
	@commands.command()
	@commands.has_any_role([Roles.MOD, Roles.ADMIN])
	async def purge(self, context, user_id: int, amount: int = 100):
		def is_from_user(message):
			return message.author.id == user_id
		try:
			deleted_messages = await context.channel.purge(limit=amount, check=is_from_user)
			await context.reply(f'Deleted {len(deleted_messages)} messages.', delete_after=5, mention_author=False)
		except HTTPException as e:
			await context.reply(f"An error occurred while deleting messages: {e}", delete_after=5, mention_author=False)
		context.message.delete()

	@commands.command(aliases=['status'], description="Change the game the bot is playing.")
	@commands.has_any_role([Roles.MOD, Roles.ADMIN])
	async def game(self, context, *, description: str) -> None:
		await self.bot.change_presence(status=Status.online, activity=Game(description))
	
	@commands.command(aliases=['stats'], description="Returns current stats of the user table.")
	@commands.has_any_role([Roles.MOD, Roles.ADMIN])
	async def databasestats(self, context) -> None:
		stats = f"`Users:{self.database.users.count()}  Badges:{self.database.badges.count()}   Quests:{self.database.quests.count()}`\n"
		size = 0
		for path, directories, files in os.walk("."):
			for file in files:
				pointer = os.path.join(path, file)
				size += os.path.getsize(pointer)
		stats += f"**`{round(size / 1024, 2):,}kB`**"
		await context.reply(stats, mention_author=False)
	
	@commands.command(aliases=['fear'],  description="")
	@commands.has_any_role([Roles.MOD, Roles.ADMIN])
	async def scare(self, context, username=None) -> None:
		try:
			mod = self.database.users.search(context.author.id)
			username = self.database.users.search(username)
			scary_string = f"*{mod.name}{"'" if mod.name[-1] == "s" else "'s"} eyes have awoken.*"
			await context.guild.get_member(username).send(scary_string)
		except:
			await context.reply("I couldn't scare them...")

	@commands.command(aliases=['test'], description="Testing... 1, 2, 3")
	@commands.is_owner()
	async def testing(self, context) -> None:
		try:
			self.database.execute("DELETE FROM Users WHERE name = ?", ("ibeefmypants",))
		except:
			await context.reply("Did not run correctly", mention_author=False)
	
	# Static commands
	async def discord(self, context) -> None:
		await context.reply("https://discord.gg/willy", mention_author=False)

	async def osu(self, context) -> None:
		await context.reply("https://osu.ppy.sh/users/3521482", mention_author=False)

	async def youtube(self, context) -> None:
		await context.reply("https://youtube.com/c/willyosu", mention_author=False)

	async def bluesky(self, context) -> None:
		await context.reply("https://bsky.app/profile/willyosu.bsky.social", mention_author=False)

	async def twitter(self, context) -> None:
		await context.reply("https://twitter.com/willyosu", mention_author=False)
	
async def setup(bot):
	await bot.add_cog(Server(bot))