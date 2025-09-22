from discord.ext import commands
from discord import AllowedMentions
import random
import re
import os

# cogs/fun.py
# - (Fun) commands.Cog for fun commands/listeners

class Fun(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot
		self.mystery_path = "./misc/mystery.txt"
		self.quotes = self.load_beetleorb("./misc/beetleorb.txt", r'\[[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}\ [0-9]{1,2}\:[0-9]{2}\:[0-9]{2}\]\ \#[a-z\d]*_?[a-z\d]+\ (.*)')
		
	def load_beetleorb(self, filename, regex: str) -> list:
		with open(filename, encoding='utf-8') as file:
			matches = re.findall(regex, file.read())
		return(matches)
	
	@commands.Cog.listener()
	async def on_message(self, context) -> None:
		mystery = os.environ.get("MYSTERY")
		if mystery and context.content.lower() == mystery:
			if os.path.getsize(self.mystery_path) > 0:
				with open(self.mystery_path, mode='r', encoding='utf-8') as file:
					name = file.read()
				await context.reply(f"<@{name}> already solved my mystery!", mention_author=False, allowed_mentions=AllowedMentions(users=False))
				return
			else:
				with open(self.mystery_path, mode='w', encoding='utf-8') as file:
					file.write(f"{context.author.id}")
				await context.reply(f"You solved my mystery. Congratulations!", mention_author=False)
				return
		return

	@commands.command(aliases=['bo', 'beetle', 'quote'],  description="Get a random beetleorb quote.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def beetleorb(self, context, *, search: str = None) -> None:
		if not search:
			await context.reply(">>> " + random.choice(self.quotes), mention_author=False)
		else:
			try:
				result = random.choice([quote for quote in self.quotes if search.lower() in quote.lower()])
				await context.reply(">>> " + result, mention_author=False)
			except:
				await context.reply("Could not find quote.", mention_author=False)
		
	@commands.command(aliases=['good', 'bad'], description="Check a user's balance.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def isitgood(self, context, *, extra = None) -> None:
		answers = {
			"It's great!": 0.15,
			"It's good": 0.25,
			"It's neutral": 0.10,
            "It's bad": 0.25,
			"It's terrible!": 0.15,
			"I don't know...": 0.03,
			"I'm a little busy...": 0.03,
			"Why are you asking me?": 0.03,
			"gorp": 0.01,
        }
		await context.reply(random.choices(list(answers.keys()), list(answers.values()), k=1)[0], mention_author=False)

	@commands.command(aliases=['mys'], description="Check a user's balance.")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def mystery(self, context, *, extra = None) -> None:
		if os.path.getsize(self.mystery_path) > 0:
			with open(self.mystery_path, mode='r', encoding='utf-8') as file:
				name = file.read()
			await context.reply(f"<@{name}> already solved my mystery!", mention_author=False, allowed_mentions=AllowedMentions(users=False))
		else:
			if extra:
				await context.reply("You don't need to use this command to solve it. Just say the answer on its own.", mention_author=False)
			else:
				await context.reply(">>> I am thinking of the name of the beast. That of the creature that lay dormant under most sun and moon. The likeness to his eponym from behind the screen is undeniable. What is the name?", mention_author=False)



async def setup(bot):
	await bot.add_cog(Fun(bot))