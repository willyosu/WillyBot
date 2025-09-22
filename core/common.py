from datetime import datetime, timezone
from discord import Embed, Colour

# core/common.py
# - common data and functions used by multiple files

# Constants
SERVER_ID = 105047038915256320
BADGE_PATH = './misc/badges/'
USERNAME_REGEX = r'^[\w-]{3,16}$'

# Text
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

# Time
def time_since_string(since: int) -> str:
	now = current_timestamp()
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
	

# Discord
def convert_mention(username): # Returns str or int
	if isinstance(username, str):
		for i in "<@>":
			username = username.replace(i, '')
		if username.isnumeric() and len(username) > 16:
			# We convert to int to signal when querying database that an id is being used
			username = int(username)
	return username

def simple_embed(title: str, description: str, fields: list = [], footer: str = None, image: str = None) -> Embed:
	embed = Embed(title=title, description=description)
	# fields is a list of name/value pair tuples
	for name, value in fields:
		embed.add_field(name=name, value=value, inline=True)
	embed.set_footer(text=footer)
	embed.set_image(url=image)
	return embed

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
