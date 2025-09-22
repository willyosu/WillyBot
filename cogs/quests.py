from discord.ext import commands
from core.database import Connection, Types
import core.common as Common

# cogs/quests.py
# - (Quest) helper class for quest specific data
# - (Quests) commands.Cog for quest related commands/listeners

class Quest:
	CHANNEL = 915359964158099456
	TIERS = {
		1: ("Easy", '🟢'), 
		2: ("Normal", '🔵'),
		3: ("Hard", '🟠'),
		4: ("Insane", '🔴'), 
		5: ("Extra", '🟣'),
		6: ("Mythic", '⚫')
	}

class Quests(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.database = Connection()
		self.database.start()
	
	@commands.command(aliases=['lq', 'ql'],  description="List of currently active quests.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def listquests(self, context, page: int = 1) -> None:
		offset, page_text = Common.paginate(page, length=self.database.quests.count_active())
		quests = self.database.quests.get_active(offset=offset)
		quest_string = []
		for quest in quests:
			tier_name, tier_icon = Quest.TIERS[quest.tier]
			quest_string.append(f"**{tier_icon} {quest.name}** - expires <t:{quest.expires}:R>")

		await context.reply(embed=Common.simple_embed(None, None, fields=[("List of active quests", '\n'.join(quest_string))], footer=page_text), mention_author=False)

	@commands.command(aliases=['quest', 'q'],  description="List information about a specified quest.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def searchquest(self, context, *, identifier) -> None:
		try:
			quest_id = self.database.quests.search(identifier)
			quest = self.database.quests.get(quest_id)
			tier_name, tier_icon = Quest.TIERS[quest.tier]
			difficulty_field = ("Difficulty", f"{tier_icon} {tier_name} ({quest.tier} QP)")
			expires_field = ("Expires", f"<t:{quest.expires}:R>")
			await context.reply(embed=Common.simple_embed(quest.name, quest.description, fields=[difficulty_field, expires_field]), mention_author=False)
		except:
			await context.reply(f"Could not find quest.", mention_author=False)

	@commands.command(aliases=['cq'], description="Create name, tier, description, expires for a quest. [NAME::TIER::DESCRIPTION::EXPIRES]")
	@commands.is_owner()
	async def createquest(self, context, *, quest_info: str) -> None:
		name, tier, description, expires = [x.strip() for x in quest_info.split("::")]
		if not tier.isdecimal() or int(tier) < 1 or int(tier) > 6:
			await context.reply("Could not understand quest tier.", mention_author=False)
			return
		tier = int(tier)
		current_timestamp = Common.current_timestamp()
		try:
			if isinstance(expires, str):
				expires = expires.strip()
				if expires.isdecimal():
					expires = int(expires)
				elif (len(expires) == 2 or len(expires) == 3) and expires[0].isdecimal():
					match (expires[-1].upper()):
						case "H":
							expires = current_timestamp + int(expires[0:-1]) * 60 * 60
						case "D":
							expires = current_timestamp + int(expires[0:-1]) * 60 * 60 * 24 
						case "W":
							expires = current_timestamp + int(expires[0:-1]) * 60 * 60 * 24 * 7
						case "M":
							expires = current_timestamp + int(expires[0:-1]) * 60 * 60 * 24 * 30
						case _:
							raise
			if expires <= current_timestamp:
				raise
		except:
			await context.reply(f"Could not understand expiry time.", mention_author=False)
			return
		
		tier_name, tier_icon = Quest.TIERS[tier]
		difficulty_field = ("Difficulty", f"{tier_icon} {tier_name} ({tier} QP)")
		expires_field = ("Expires", f"<t:{expires}:R>")

		channel = await self.bot.fetch_channel(Quest.CHANNEL)
		message = await channel.send(embed=Common.simple_embed(name, description, fields=[difficulty_field, expires_field]))
		
		quest = Types.Quest(message.id, name, tier, description, expires)
		try:
			self.database.quests.create(quest)
			quest = self.database.quests.get(quest.id)
			await context.reply(f"Created quest \'{quest.name}\'. `ID: {quest.id}`", mention_author=False)
		except:
			await context.reply(f"Could not create quest.", mention_author=False)
	
	@commands.command(aliases=['uq'], description="Update attribute for a quest. [NAME::ATTR::VALUE]")
	@commands.is_owner()
	async def updatequest(self, context, *, quest_info: str) -> None:
		identifier, attribute, value = [x.strip() for x in quest_info.split("::")]
		attribute = attribute.lower()
		try:
			quest_id = self.database.quests.search(identifier)
			self.database.quests.update(quest_id, attribute, value)
			quest = self.database.quests.get(quest_id)
			
			tier_name, tier_icon = Quest.TIERS[quest.tier]
			difficulty_field = ("Difficulty", f"{tier_icon} {tier_name} ({quest.tier} QP)")
			expires_field = ("Expires", f"<t:{quest.expires}:R>")
			
			channel = await self.bot.fetch_channel(Quest.CHANNEL)
			message = await channel.fetch_message(quest.id)
			await message.edit(embed=Common.simple_embed(quest.name, quest.description, fields=[difficulty_field, expires_field]))
			
			await context.reply(f"Changed \"{attribute}\" of `ID:{quest.id}` to `{value}`.", mention_author=False)
		except:
			await context.reply(f"Could not update quest.", mention_author=False)

	@commands.command(aliases=['dq'], description="Deletes a quest.")
	@commands.is_owner()
	async def deletequest(self, context, *, identifier: str) -> None:
		try:
			quest_id = self.database.quests.search(identifier)
			quest = self.database.quests.get(quest_id)
			self.database.quests.delete(quest_id)
			channel = await self.bot.fetch_channel(Quest.CHANNEL)
			message = await channel.fetch_message(quest_id)
			await message.delete()

			await context.reply(f"Deleted quest \'{quest.name}\'. `ID: {quest.id}`.", mention_author=False)
		except:
			await context.reply(f"Could not find quest.", mention_author=False)

	@commands.command(aliases=['qp', 'qs'],  description="List information about a specified quest.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def queststats(self, context, identifier=None) -> None:
		identifier = context.author.id if not identifier else Common.convert_mention(identifier)
		try:
			user_id = self.database.users.search(identifier)
			user = self.database.users.get(user_id)
			try:
				user_quests = self.database.userquests.get(user.id)
				user_quests_string = []
				total_qp = 0
				for i in range(1, len(user_quests)):
					tier_name, tier_icon = Quest.TIERS[i]
					total_qp += user_quests[i] * (i)
					user_quests_string.append(f"**{tier_icon} {tier_name}**  -  **{user_quests[i]}** ({user_quests[i] * (i)} QP)")
				qp_rank = self.database.userquests.qp_rank(total_qp)
				await context.reply(embed=Common.simple_embed(f"{user.name}", None, fields=[("Quest points", f"{total_qp} QP  **`#{qp_rank}`**"), (f"**{sum(user_quests[1:])} quests completed**", '\n'.join(user_quests_string))]), mention_author=False)
			except:
				await context.reply(f"User has not completed any quests.", mention_author=False)
		except:
			await context.reply(f"Could not find user.", mention_author=False)

	@commands.command(aliases=['qlb', 'tq'],  description="List of highest QP users.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def topqp(self, context, page: int = 1) -> None:
		offset, page_text = Common.paginate(page, length=self.database.userquests.count())
		user_qps = self.database.userquests.qp_ranking(offset=offset)
		user_string = []
		for user_id, count in user_qps:
			offset += 1
			user = self.database.users.get(user_id)
			user_string.append(f"`#{offset}`  **{user.name}**  ({count:,})")
		await context.reply(embed=Common.simple_embed(None, None, fields=[("List of highest qp users", '\n'.join(user_string))], footer=page_text), mention_author=False)

	@commands.command(aliases=['aqp'], description="Add quest points to a specified user.")
	@commands.is_owner()
	async def addquestpoints(self, context, identifier, tier, amount = 1) -> None:
		identifier = context.author.id if not identifier else Common.convert_mention(identifier)
		try:
			user_id = self.database.users.search(identifier)
			user = self.database.users.get(user_id)
			if not tier.isdecimal() or int(tier) < 1 or int(tier) > 5:
				await context.reply("Could not understand quest tier.", mention_author=False)
				return
			tier = int(tier)
			user_quests = self.database.userquests.get(user.id)
			if not user_quests:
				self.database.userquests.create(user.id)
				user_quests = (user_id, 0, 0, 0, 0, 0)
			self.database.userquests.update(user.id, Quest.TIERS[tier][0].lower(), user_quests[tier] + amount)
			await context.reply(f"Added {tier * amount} quest points to {user.name}!", mention_author=False)
		except:
			await context.reply(f"Could not add quest points.", mention_author=False)

async def setup(bot):
	await bot.add_cog(Quests(bot))