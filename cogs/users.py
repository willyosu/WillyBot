from discord.ext import commands
from discord import Embed, File
from core.database import Connection, Types
from core.common import Data, Time, Level, Embeds
import re
from PIL import Image, ImageDraw, ImageColor

# cogs/users.py
# - (Users) commands.Cog for user related commands/listeners
	
class Users(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot
		self.database = Connection()
		self.database.start()

	def register_user(self, discord_user):
		name = ''.join(char if (char.isalnum() or char in "-_") else '' for char in discord_user.name)
		if(int(discord_user.discriminator) > 0):
			name += discord_user.discriminator
		self.database.users.create(Types.User(discord_user.id, name, None, discord_user.joined_at.timestamp(), Time.current_timestamp(), 0))

	@commands.Cog.listener()
	async def on_message(self, context) -> None:
		try:
			self.database.users.search(context.author.id)
		except:
			self.register_user(context.author)
		user = self.database.users.get(context.author.id)
		current_time = Time.current_timestamp()
		self.database.users.update(user.id, 'active', current_time)
		if current_time - user.active < 5 or context.author.bot:
			return
		
		# Each user has a random chance to earn 1-5 xp with each message
		bonus_xp = min(4, 1 + int(len(context.content) / 20))
		if context.attachments:
			bonus_xp += 1
		if Time.is_different_day(user.active, current_time):
			bonus_xp += Level.level_from_xp(user.xp)
		self.database.users.update(user.id, 'xp', user.xp + bonus_xp)

	@commands.command(aliases=['p', 'user', 'u'],  description="Check a user's server profile.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def profile(self, context, identifier = None) -> None:
		try:
			identifier = context.author.id if not identifier else Data.convert_mention(identifier)
			discord_server = await self.bot.fetch_guild(Data.SERVER_ID)
			try:
				user_id = self.database.users.search(identifier)
			except:
				discord_user = await discord_server.fetch_member(identifier)
				self.register_user(discord_user)
				user_id = discord_user.id
			
			user = self.database.users.get(user_id)
			user_badges = self.database.userbadges.get_image_list(user.id)
			
			PADDING = 6
			BADGE_WIDTH = 80
			BADGE_HEIGHT = 40
			BADGES_PER_ROW = 4
			XP_HEIGHT = PADDING * 2 + 4
			IMAGE_WIDTH = BADGES_PER_ROW * (BADGE_WIDTH + PADDING) + PADDING

			image = Image.new('RGBA', (IMAGE_WIDTH, int((len(user_badges) + BADGES_PER_ROW - 1) / BADGES_PER_ROW) * (BADGE_HEIGHT + PADDING) + XP_HEIGHT + PADDING), 0)
			
			current_level, prev_xp, next_xp = Level.progress(user.xp)
			bar = ImageDraw.Draw(image)
			bar.rectangle((PADDING, PADDING, IMAGE_WIDTH - PADDING, PADDING + 4), fill=ImageColor.getrgb("#C0C0C0"))
			bar.rectangle((PADDING, PADDING, PADDING + int((IMAGE_WIDTH - PADDING)*(user.xp - prev_xp)/(next_xp - prev_xp)), PADDING + 4), fill=ImageColor.getrgb((str(Level.level_color(current_level)))))
			
			for i in range(len(user_badges)):
				image.paste(Image.open(Data.BADGE_PATH + user_badges[i][0]), (PADDING + (BADGE_WIDTH + PADDING)*(i % BADGES_PER_ROW), int(i / BADGES_PER_ROW) * (BADGE_HEIGHT + PADDING) + (XP_HEIGHT) + PADDING))
			
			image.save(f'./temp/{str(user.id)}.png')
			file = File(f'./temp/{str(user.id)}.png', filename="profile.png")

			embed = Embed(title = f"**{user.name}**\n{user.title if user.title else ''}", description = '\n')
			try:
				discord_user = await discord_server.fetch_member(int(user_id))
				embed.set_thumbnail(url=discord_user.display_avatar)
				if discord_user.bot:
					embed.description += "-# **BOT USER  🤖**"
				if not user.name.lower() == discord_user.display_name.lower():
					embed.description += f"-# *also known as* ***{Data.cutoff_text(Data.sanitize(discord_user.display_name), 32)}***"
			except:
				embed.description += "-# **INACTIVE USER  ⛔**"

			embed.set_footer(text=(f"Joined {Time.time_since_string(user.joined)}  •  Active {Time.time_since_string(user.active)}"))
			embed.add_field(name=f"Level {current_level:,}", value=f"{user.xp:,}xp  **`#{self.database.users.xp_rank(user.xp)}`**", inline=True)
			embed.color = Level.level_color(current_level)
			embed.set_image(url=f'attachment://profile.png')
			
			await context.reply(embed=embed, file=file, mention_author=False)
		except:
			await context.reply("Could not find user.", mention_author=False)


	@commands.command(aliases=['cn'], description="Change the username of a specified user.")
	@commands.is_owner()
	async def changename(self, context, old_name: str, new_name: str) -> None:
		try:
			user_id = self.database.users.search(old_name)
		except:
			await context.reply(f"Could not find user \'{old_name}\'.", mention_author=False)
			return
		try:
			if self.database.users.search(new_name) and old_name.lower() == new_name.lower():
				raise
			else:
				await context.reply(f"Username \'{new_name}\' already in use.", mention_author=False)
				return
		except:
			if re.match(Data.USERNAME_REGEX, new_name):
				self.database.users.update(user_id, 'name', new_name)
				await context.reply(f"Successfully updated username to {new_name}!", mention_author=False)
			else:
				await context.reply("Please use a username that is between 3-20 characters, and does not contain symbols.", mention_author=False)

	@commands.command(aliases=['ct'], description="Change the title of a specified user.")
	@commands.is_owner()
	async def changetitle(self, context, identifier, *, title: str = None) -> None:
		try:
			user_id = self.database.users.search(identifier)
			self.database.users.update(user_id, 'title', title)
			await context.reply("Successfully updated user title!", mention_author=False)
		except:
			await context.reply(f"Could not find user.", mention_author=False)
	
	@commands.command(aliases=['cj', 'changejoin', 'updatejoin'], description="Change join date of a specified user (YYYY-MM-DD).")
	@commands.is_owner()
	async def changejoined(self, context, identifier, joined: str) -> None:
		try:
			user_id = self.database.users.search(identifier)
			try:
				joined = Time.date_to_timestamp(joined)
			except:
				await context.reply("Malformed date.", mention_author=False)
				return
			self.database.users.update(user_id, 'joined', joined)
			await context.reply("Successfully updated join date!", mention_author=False)
		except:
			await context.reply(f"Could not find user.", mention_author=False)
	
	@commands.command(aliases=['lt', 'titles'],  description="List of all unique user titles.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def listtitles(self, context, page: int = 1) -> None:
		# Should paginate this later
		titles = self.database.users.distinct_title_list()
		await context.reply(embed=Embeds.simple_embed(None, None, fields=[("List of unique user titles", '\n'.join(titles))]), mention_author=False)
	
	@commands.command(aliases=['lv', 'lvl'],  description="Returns a user's xp and level.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def level(self, context, identifier = None) -> None:
		identifier = context.author.id if not identifier else Embed.convert_mention(identifier)
		try:
			user_id = self.database.users.search(identifier)
			user = self.database.users.get(user_id)
			current_level, prev_xp, next_xp = Level.progress(user.xp)
			await context.reply(f"{user.name} is level {current_level:,} with {user.xp:,}xp ({next_xp - user.xp:,}xp until next level!)", mention_author=False)
		except:
			await context.reply("Could not find user.", mention_author=False)
	
	@commands.command(aliases=['lvlcalc', 'lvlc'],  description="Calculate how much xp is needed to reach a level.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def levelcalc(self, context, amount: int = 1) -> None:
		amount = abs(amount)
		if amount <= 1000:
			await context.reply(f"Level {amount:,} = {Level.xp_from_level(amount):,}xp", mention_author=False)
		else:
			await context.reply(f"That's a little too high level for me...", mention_author=False)
	
	@commands.command(aliases=['xpc'],  description="Calculate how much xp is needed to reach a level.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def xpcalc(self, context, amount: int = 1) -> None:
		amount = abs(amount)
		if amount <= 50000000:
			await context.reply(f"{amount:,}xp = Level {Level.level_from_xp(amount):,}", mention_author=False)
		else:
			await context.reply(f"That's a little too much xp for me...", mention_author=False)

	@commands.command(aliases=['txp', 'tl', 'lb'],  description="List of highest xp users.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def topxp(self, context, page: int = 1) -> None:
		offset, page_text = Data.paginate(page, length=self.database.users.count())
		user_xps = self.database.users.xp_ranking(offset=offset)
		user_string = []
		for user, count in user_xps:
			offset += 1
			user = self.database.users.get(user)
			user_string.append(f"`#{offset}`  **{user.name}**  {count:,} (lvl {Level.level_from_xp(count):,})")
		await context.reply(embed=Embeds.simple_embed(None, None, fields=[("List of highest xp users", '\n'.join(user_string))], footer=page_text), mention_author=False)
	
	@commands.command(aliases=['axp'], description="Add xp to specified user.")
	@commands.is_owner()
	async def addxp(self, context, username: str, xp: int) -> None:
		try:
			user_id = self.database.users.search(username)
			user = self.database.users.get(user_id)
			self.database.users.update(user.id, "xp", user.xp + xp)
			await context.reply(f"Added `{xp}xp` to user! Now `{user.xp + xp}xp` total.", mention_author=False)
		except:
			await context.reply(f"Could not find user.", mention_author=False)

async def setup(bot):
	await bot.add_cog(Users(bot))