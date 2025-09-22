from discord.ext import commands
from discord import File
from core.database import Connection, Types
import core.common as Common

# cogs/badges.py
# - (Badges) commands.Cog for user badge related commands/listeners

class Badges(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot
		self.database = Connection()
		self.database.start()
	
	@commands.command(aliases=['b'],  description="List of all users with a specified badge.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def badge(self, context, *, identifier) -> None:
		try:
			badge_id = self.database.badges.search(identifier)
			badge = self.database.badges.get(badge_id)
			user_list = self.database.userbadges.user_list(badge.id)
			user_list = ', '.join([x[0] for x in user_list])
			file = File(Common.BADGE_PATH + badge.image, filename="badge.png")
			await context.reply(embed=Common.simple_embed(badge.name, f'*{badge.description}*', fields=[("Owned by", user_list)], image="attachment://badge.png" ), file=file, mention_author=False)
		except:
			await context.reply(f"Could not find badge.", mention_author=False)
		
	@commands.command(aliases=['ab'], description="Add badge to a specified user.")
	@commands.is_owner()
	async def addbadge(self, context, username, *, identifier) -> None:
		try:
			user_id = self.database.users.search(username)
		except:
			await context.reply(f"Could not find user.", mention_author=False)
			return
		try:
			badge_id = self.database.badges.search(identifier)
		except:
			await context.reply(f"Could not find badge.", mention_author=False)
		
		self.database.userbadges.create(user_id, badge_id)
		await context.reply(f"Added badge id \'{badge_id}\' to user!", mention_author=False)

	@commands.command(aliases=['rb'], description="Remove badge from a specified user.")
	@commands.is_owner()
	async def removebadge(self, context, username, *, identifier) -> None:
		try:
			user_id = self.database.users.search(username)
		except:
			await context.reply(f"Could not find user.", mention_author=False)
			return
		try:
			badge_id = self.database.badges.search(identifier)
		except:
			await context.reply(f"Could not find badge.", mention_author=False)

		self.database.userbadges.delete(user_id, badge_id)
		await context.reply(f"Removed badge id \'{badge_id}\' from user!", mention_author=False)
	
	@commands.command(aliases=['cb'],  description="Create name and image for a badge. [NAME::IMAGE]")
	@commands.is_owner()
	async def createbadge(self, context, *, badge_info: str) -> None:
		badge = Types.Badge(None, *[x.strip() for x in badge_info.split("::")]) 
		try:
			self.database.badges.create(badge)
			badge = self.database.badges.search(badge.name)
			badge = self.database.badges.get(badge)
			await context.reply(f"Created badge \'{badge.name}\' with image \'{badge.image}\'. `ID: {badge.id}`", mention_author=False)
		except:
			await context.reply(f"Could not create badge.", mention_author=False)
	
	@commands.command(aliases=['db'],  description="Delete name and image for a badge.")
	@commands.is_owner()
	async def deletebadge(self, context, *, identifier) -> None:
		try:
			badge_id = self.database.badges.search(identifier)
			badge = self.database.badges.get(badge_id)
			self.database.badges.delete(badge.id)
			await context.reply(f"Deleted badge \'{badge.name}\' with image \'{badge.image}\'. `ID: {badge.id}`.", mention_author=False)
		except:
			await context.reply(f"Could not find badge.", mention_author=False)
		
	@commands.command(aliases=['ub', 'changebadge'],  description="Update attribute for a badge. [NAME::ATTR::VALUE]")
	@commands.is_owner()
	async def updatebadge(self, context, *, badge_info: str) -> None:
		identifier, attribute, value = [x.strip() for x in badge_info.split("::")]
		attribute = attribute.lower()
		try:
			badge_id = self.database.badges.search(identifier)
			self.database.badges.update(badge_id, attribute, value)
			await context.reply(f"Changed \"{attribute}\" of `ID:{badge_id}` to `{value}`.", mention_author=False)
		except:
			await context.reply(f"Could not update badge.", mention_author=False)

	@commands.command(aliases=['bl', 'badges', 'badgelist'],  description="List all awarded badges.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def listbadges(self, context, page: int = 1) -> None:
		offset, page_text = Common.paginate(page, length=self.database.userbadges.count_badges())
		badge_counts = self.database.userbadges.badge_counts(offset=offset)
		badge_string = []
		for badge_id, count in badge_counts:
			badge = self.database.badges.get(badge_id)
			badge_string.append(f"- {badge.name} **({count:,})** \n-# *{Common.cutoff_text(badge.description, 52)}*")
		await context.reply(embed=Common.simple_embed(None, None, fields=[("List of all awarded badges", '\n'.join(badge_string))], footer=page_text), mention_author=False)
	
	@commands.command(aliases=['tb'],  description="List all awarded badges.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def topbadges(self, context, page: int = 1, special: str = None) -> None:
		offset, page_text = Common.paginate(page, length=self.database.userbadges.count_users())
		user_counts = self.database.userbadges.user_counts(offset=offset)
		user_string = []
		for user, count in user_counts:
			offset += 1
			user = self.database.users.get(user)
			user_string.append(f"`#{offset}`  **{user.name}**  ({count:,})")
		await context.reply(embed=Common.simple_embed(None, None, fields=[("List of most decorated users", '\n'.join(user_string))], footer=page_text), mention_author=False)
			


async def setup(bot):
	await bot.add_cog(Badges(bot))