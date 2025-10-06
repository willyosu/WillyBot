from discord.ext import commands, tasks
from core.database import Connection
from core.common import Time
import os
import shutil

# cogs/tasks.py
# - (Tasks) commands.Cog primarily holding database task loops

class Tasks(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot
		self.database = Connection()
		self.database.start()

		self.backup_database.start()
		self.delete_temp_files.start()
		self.cleanup_users.start()
		self.cleanup_quests.start()

	@tasks.loop(hours=24)
	async def backup_database(self) -> None:
		code = 'TASK:BACKUP >'
		print(f"{code} Running database backup...")
		try:
			now = Time.current_timestamp()
			for path, directories, files in os.walk("./backups"):
				for file in files:
					pointer = os.path.join(path, file)
					if int(os.path.getmtime(pointer)) < (now - 60 * 60 * 24 * 7):
						os.remove(pointer)
		except:
			raise Exception(f"{code} ERROR with backup cleanup.")
		try:
			print(f"{code} Backing up current database.")
			shutil.copy("./willybot.db", f"./backups/{now}.db")
		except:
			raise Exception(f"{code} ERROR with backup creation.")
	
	@tasks.loop(hours=1)
	async def delete_temp_files(self) -> None:
		code = 'TASK:TEMPFILES >'
		print(f"{code} Running temp file deletion...")
		try:
			now = Time.current_timestamp()
			for path, directories, files in os.walk("./temp"):
				for file in files:
					pointer = os.path.join(path, file)
					if int(os.path.getmtime(pointer)) < (now - 60):
						os.remove(pointer)
		except:
			raise Exception(f"{code} ERROR with temp file deletion.")

	@tasks.loop(hours=24)
	async def cleanup_users(self):
		code = 'TASK:USERS >'
		print(f"{code} Running users table cleanup...")
		try:
			self.database.execute("DELETE FROM Users WHERE xp <= 0 AND active <= ?", (Time.current_timestamp() - (60 * 60 * 24 * 30),))
		except:
			raise Exception(f"{code} Error with users table cleanup.")

	@tasks.loop(hours=1)
	async def cleanup_quests(self):
		code = 'TASK:QUESTS >'
		print(f"{code} Running quests table cleanup...")
		try:
			expiring_quests = self.database.quests.get_expiring()
			for quest in expiring_quests:
				print(quest.name)
				try:
					channel = await self.bot.fetch_channel(915359964158099456)
					message = await channel.fetch_message(quest.id)
					await message.delete()
				except:
					print(f"{code} Could not get quest message with id of `{quest.id}`.")
				self.database.quests.delete(quest.id)
		except:
			raise Exception(f"{code} Error with quests table cleanup.")

async def setup(bot):
	await bot.add_cog(Tasks(bot))