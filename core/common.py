from datetime import datetime, timezone
from discord import Embed, Colour
import math

# core/common.py
# - (Data) common data and functions used by multiple files
# - (Time) time related functions
# - (Embed) for easy use of discord.py embeds
# - (Level) level related functions
# - (Roles) server roles structure
# - (Quest) quest data structure

# This file is kind of an eclectic mess... fix it later

class Data:
	SERVER_ID = 105047038915256320
	BADGE_PATH = './misc/badges/'
	USERNAME_REGEX = r'^[\w-]{3,16}$'
	EMOTES = {
		"XH": "<:SSH_rank:1422021467234635786>",
		"X": "<:SS_rank:1422021442916061184>",
		"SH": "<:SH_rank:1422021418903797780>",
		"S": "<:S_rank:1422021393121415218>",
		"A": "<:A_rank:1422021305124917268>",
		"B": "<:B_rank:1422021334103494666>",
		"C": "<:C_rank:1422021352571011292>",
		"D": "<:D_rank:1422021372577583196>",
		"miss": "<:miss:1422021257150595114>",
		"osu": "<:osu:1422076390383026257>",
		"catch": "<:catch:1422076452517445712>",
		"taiko": "<:taiko:1422076490853519382>",
		"mania": "<:mania:1422076532981235743>",
		"RANKED": "<:ranked:1422047717089214495>",
		"QUALIFIED": "<:qualified:1422047724051890206>",
		"LOVED": "<:loved:1422047733874819183>",
		"GRAVEYARDED": "**UNRANKED**"
	}

	def sanitize(text: str) -> str:
		for x in "<>|@&#[]():*_-`~":
			text = text.replace(x, '\\' + x)
		return text

	def cutoff_text(text: str, max_length: int):
		return text if len(text) <= max_length else text[:max_length - 3] + "..."

	def paginate(page: int = 1, size: int = 10, length: int = 0) -> tuple:
		max_page = int(length / size + 1)
		page = 1 if page < 1 or page > max_page else page
		offset = 10 * (page - 1)
		page_text =  f"Page {page} of {max_page}   ({length} total results)"
		return (offset, page_text)
	
	def convert_mention(username): # Returns str or int
		if isinstance(username, str):
			for i in "<@>":
				username = username.replace(i, '')
			if username.isnumeric() and len(username) > 16:
				# We convert to int to signal when querying database that an id is being used
				username = int(username)
		return username

class Time:
	def time_since_string(since: int) -> str:
		now = Time.current_timestamp()
		if since < 1451635200: # 2016-01-01
			return "at the beginning"
		units = "minutes"
		elapsed_time = (now - since) / 60
		if elapsed_time < 5:
			return "now"
		if elapsed_time > 60: # 1 hour
			elapsed_time /= 60
			units = "hours"
			if elapsed_time > 24: # 1 day
				elapsed_time /= 24
				units = "days"
				if elapsed_time > (365.24/12): # 1 month
					elapsed_time /= (365.24/12)
					units = "months"
					if elapsed_time > 12: # 1 year
						elapsed_time /= 12
						units = "years"
		elapsed_time = int(elapsed_time)
		if elapsed_time == 1:
			units = units[0:-1]
		return f"{elapsed_time} {units} ago"

	def current_timestamp() -> int:
		return int(datetime.now(tz=timezone.utc).timestamp())

	def is_different_day(old: int, new: int) -> bool:
		old = datetime.fromtimestamp(old, tz=timezone.utc)
		new = datetime.fromtimestamp(new, tz=timezone.utc)
		return not (old.date() == new.date())

	def date_to_timestamp(date: str) -> int:
		date = datetime.fromisoformat(date)
		date.replace(tzinfo=timezone.utc)
		return int(date.timestamp())
	
class Embeds:
	def simple_embed(title: str, description: str, thumbnail: str = None, fields: list = [], inline: bool = True, footer: str = None, image: str = None) -> Embed:
		embed = Embed(title=title, description=description)
		# fields is a list of name/value pair tuples
		for name, value in fields:
			embed.add_field(name=name, value=value, inline=inline)
		embed.set_thumbnail(url=thumbnail)
		embed.set_footer(text=footer)
		embed.set_image(url=image)
		return embed

class Level:
	LEVEL_FACTOR = 50  # How much xp each level is increased by

	def level_from_xp(xp: int) -> int:
		return int(math.sqrt(xp / Level.LEVEL_FACTOR))

	def xp_from_level(level: int) -> int:
		return int(Level.LEVEL_FACTOR * math.pow(level, 2))

	def progress(current_xp:int) -> tuple:
		current_level = Level.level_from_xp(current_xp)
		prev_level_xp = Level.xp_from_level(current_level)
		next_level_xp = Level.xp_from_level(current_level + 1)
		return (current_level, prev_level_xp, next_level_xp)

	def level_color(level: int) -> Colour:
		# Currently only used to color profile embeds, maybe more in the future
		match (round(level / 5) * 5):
			case 0:
				return Colour.darker_grey()
			case 5:
				return Colour.light_grey()
			case 10:
				return Colour.dark_green()
			case 15:
				return Colour.green()
			case 20:
				return Colour.dark_teal()
			case 25:
				return Colour.teal()
			case 30:
				return Colour.dark_blue()
			case 35:
				return Colour.blue()
			case 40:
				return Colour.blurple()
			case 45:
				return Colour.og_blurple()
			case 50:
				return Colour.dark_purple()
			case 55:
				return Colour.purple()
			case 60:
				return Colour.dark_magenta()
			case 65:
				return Colour.magenta()
			case 70:
				return Colour.dark_red()
			case 75:
				return Colour.red()
			case 80:
				return Colour.dark_orange()
			case 85:
				return Colour.orange()
			case 90:
				return Colour.dark_gold()
			case 95:
				return Colour.gold()
			case _: # level < 100:
				return Colour.from_rgb(254, 212, 41)

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
