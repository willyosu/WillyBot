import sqlite3
from core.common import current_timestamp

# core/database.py:
# - (Connection) database connection/handler 
# - (Types) schema class model for easily interacting with data 
# - (Tables) namespace implementing table specific methods

class Connection:
	def __init__(self) -> None:
		self.connection = None
		self.cursor = None
	
	def start(self):
		self.__connect__()
		self.__build__()
	
	def __connect__(self) -> None:
		self.connection = sqlite3.connect("./willybot.db")
		self.cursor = self.connection.cursor()
		self.__set_table_commands__()

	def __del__(self):
		self.connection.commit()
		self.connection.close()
	
	def __build__(self):
		self.execute("CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, name TEXT UNIQUE, title TEXT, joined INTEGER, active INTEGER, xp INTEGER DEFAULT 0)")
		self.execute("CREATE TABLE IF NOT EXISTS Badges (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, image TEXT, description TEXT)")
		self.execute("CREATE TABLE IF NOT EXISTS UserBadges (user INTEGER, badge INTEGER, PRIMARY KEY (user, badge), FOREIGN KEY (user) REFERENCES Users(id) ON UPDATE CASCADE, FOREIGN KEY (badge) REFERENCES Badges(id) ON UPDATE CASCADE)")
		self.execute("CREATE TABLE IF NOT EXISTS Quests (id INTEGER PRIMARY KEY UNIQUE, name TEXT UNIQUE, tier INTEGER, description TEXT, expires INTEGER)")
		self.execute("CREATE TABLE IF NOT EXISTS UserQuests (user INTEGER, easy INTEGER, normal INTEGER, hard INTEGER, insane INTEGER, extra INTEGER, FOREIGN KEY (user) REFERENCES Users(id) ON UPDATE CASCADE)")

	def __set_table_commands__(self):
		self.users = Tables.Users(self)
		self.badges = Tables.Badges(self)
		self.userbadges = Tables.UserBadges(self)
		self.quests = Tables.Quests(self)
		self.userquests = Tables.UserQuests(self)

	def execute(self, command: str, values: tuple = (), fetch = False):
		try:
			self.cursor = self.cursor.execute(command, values)
			self.connection.commit()
			# fetch True should return ALL from table
			if fetch:
				if isinstance(fetch, bool):
					value = self.cursor.fetchall()
				else:
					if fetch == 1:
						value = self.cursor.fetchone()
						if len(value) == 1:
							value = value[0]
					else:
						value = self.cursor.fetchmany(fetch)
				return value
			else:
				return
		except:
			raise Exception("Error in Connection.execute()")
	
	def create(self, table: str, attributes: tuple, values: tuple) -> None:
		command = f"INSERT INTO {table} ({','.join(attributes)}) VALUES ({','.join(['?'] * len(attributes))})"
		self.execute(command, values)
	
	def get(self, table: str, _id: int, key: str = 'id') -> tuple:
		command = f"SELECT * FROM {table} WHERE {key} = ?"
		try:
			return self.execute(command, (_id,), fetch=1)
		except:
			raise NotFound(f"Could not find {table} entries with key {key}.")
	
	def get_specific(self, table: str, attributes: tuple, values: tuple) -> tuple:
		command = f"SELECT * FROM {table} WHERE {' AND '.join([x + ' = ?' for x in attributes])}"
		try:
			return self.execute(command, values, fetch=1)
		except:
			raise NotFound(f"Could not find {table} entries with keys {attributes}.")
	
	def search(self, table: str, identifier, strict = False) -> int:
		if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isnumeric()):
			identifier = int(identifier)
			command = f"SELECT id FROM {table} WHERE id = ?"
		else:
			if strict:
				command = f"SELECT id FROM {table} WHERE name = ? COLLATE NOCASE"
			else:
				command = f"SELECT id FROM {table} WHERE LOWER(name) LIKE LOWER(?)"
				identifier = f"%{identifier}%"
		try:
			_id = self.execute(command, (identifier,), fetch=1)
		except:
			raise NotFound(f"Could not find {table} entry with identifier {identifier}.")
		if not _id:
			raise NotFound(f"Could not find {table} entry with identifier {identifier}.")
		else:
			return _id
	
	def update(self, table: str, attributes: tuple, attribute: str, _id: int, value, key: str = 'id') -> None:
		if attribute in attributes:
			command = f"UPDATE {table} SET {attribute} = ? WHERE {key} = ?"
			self.execute(command, (value, _id))
		else:
			raise NotFound(f"No column \'{attribute}\' in table {table}")
		
	def delete(self, table: str, _id: int, key: str = 'id') -> None:
		command = f"DELETE FROM {table} WHERE {key} = ?"
		self.execute(command, (_id,))
	
	def delete_specific(self, table: str, attributes: tuple, values: tuple) -> tuple:
		command = f"DELETE FROM {table} WHERE {' AND '.join([x + ' = ?' for x in attributes])}"
		return self.execute(command, values, fetch=1)

	def count(self, table: str, key: str = 'id', distinct = False) -> int:
		command = f"SELECT COUNT({'DISTINCT ' + key if distinct else key}) as count FROM {table}"
		return self.execute(command, fetch=1)



class NotFound(Exception):
	pass



class Types:
	class User:
		def __init__(self, id: int = None, name: str = None, title: str = None, joined: int = None, active: int = None, xp: int = 0) -> None:
			self.id = id
			self.name = name
			self.title = title
			self.joined = joined
			self.active = active
			self.xp = xp
	
	class Badge:
		def __init__(self, id: int = None, name: str = None, image: str = None, description: str = None):
			self.id = id
			self.name = name
			self.image = image
			self.description = description

	class Quest:
		def __init__(self, id: int = None, name: str = None, tier: int = None, description: str = None, expires: int = None):
			self.id = id
			self.name = name
			self.tier = tier
			self.description = description
			self.expires = expires

class Tables:
	class Table:
		def __init__(self, connection: Connection, name: str, attributes: tuple, key: str = 'id'):
			self.connection = connection
			self.name = name
			self.attributes = attributes
			self.key = key

		def delete(self, _id: int) -> None:
			self.connection.delete(self.name, _id)
		
		def update(self, _id: int, attribute: str, value) -> None:
			self.connection.update(self.name, self.attributes, attribute, _id, value, key=self.key)

		def count(self) -> int:
			return self.connection.count(self.name, key=self.key)
	
	class BaseTable(Table):
		def __init__(self, connection, name, attributes, type = tuple):
			super().__init__(connection, name, attributes)
			self.type = type

		def search(self, identifier) -> int:
			return self.connection.search(self.name, identifier)
		
		def get(self, _id: int):
			return self.type(*(self.connection.get(self.name, _id)))

	class RelationTable(Table):
		def __init__(self, connection, name, attributes):
			super().__init__(connection, name, attributes, key = 'user')

		def get(self, _id: int):
			return (self.connection.get(self.name, _id, key=self.key))

	class Users(BaseTable):
		def __init__(self, connection: Connection):
			super().__init__(connection, name='Users', attributes=('id', 'name', 'title', 'joined', 'active', 'xp'), type=Types.User)

		def create(self, user: Types.User) -> None:
			self.connection.create(self.name, self.attributes, (user.id, user.name, None, user.joined, user.active, 0))

		def search(self, identifier) -> int:
			return self.connection.search(self.name, identifier, strict=True)
		
		# Custom
		def xp_rank(self, xp: int) -> int:
			return self.connection.execute("SELECT COUNT(id) FROM Users WHERE xp >= ?", (xp,), fetch=1)
		
		def xp_ranking(self, offset: int = 0, size: int = 10) -> list:
			return self.connection.execute("SELECT id, xp FROM Users ORDER BY xp DESC LIMIT ? OFFSET ?", (size, offset), fetch=True)

		def distinct_title_list(self) -> list:
			return self.connection.execute("SELECT DISTINCT title FROM Users ORDER BY title", fetch=True)
	
	class Badges(BaseTable):
		def __init__(self, connection):
			super().__init__(connection, name='Badges', attributes=('id', 'name', 'image', 'description'), type=Types.Badge)

		def create(self, badge: Types.Badge) -> None:
			self.connection.create(self.name, self.attributes, (None, badge.name, badge.image, badge.description))
	
	class UserBadges(RelationTable):
		def __init__(self, connection):
			super().__init__(connection, name='UserBadges', attributes=('user', 'badge'))

		def create(self, user_id: int, badge_id: int) -> None:
			self.connection.create(self.name, self.attributes, (user_id, badge_id))

		def get(self, user_id: int, badge_id: int) -> tuple:
			return self.connection.get_specific(self.name, ('user', 'badge'), (user_id, badge_id))
		
		def delete(self, user_id: int, badge_id: int) -> None:
			self.connection.delete_specific(self.name, ('user', 'badge'), (user_id, badge_id))

		def count_users(self) -> int:
			return self.connection.count(self.name, key='user', distinct=True)
		
		def count_badges(self) -> int:
			return self.connection.count(self.name, key='badge', distinct=True)

		#Custom
		def get_image_list(self, user_id: int) -> list:
			return self.connection.execute("SELECT image FROM UserBadges ub INNER JOIN Badges b ON ub.badge = b.id WHERE ub.user = ?", (user_id,), fetch=True)
		
		def user_list(self, badge_id: int) -> list:
			return self.connection.execute("SELECT name FROM UserBadges ub INNER JOIN Users u ON ub.user = u.id WHERE badge = ?", (badge_id,), fetch=True)
		
		def badge_counts(self, offset: int = 0, size: int = 10) -> list:
			return self.connection.execute("SELECT badge, COUNT(badge) AS count FROM UserBadges GROUP BY badge ORDER BY count DESC LIMIT ? OFFSET ?", (size, offset), fetch=True)
		
		def user_counts(self, offset: int = 0, size: int = 10) -> list:
			return  self.connection.execute("SELECT user, COUNT(user) AS count FROM UserBadges GROUP BY user ORDER BY count DESC LIMIT ? OFFSET ?", (size, offset), fetch=True)

	class Quests(BaseTable):
		def __init__(self, connection):
			super().__init__(connection, name='Quests', attributes=('id', 'name', 'tier', 'description', 'expires'), type=Types.Quest)

		def create(self, quest: Types.Quest) -> None:
			self.connection.create(self.name, self.attributes, (quest.id, quest.name, quest.tier, quest.description, quest.expires))
		
		# Custom
		def count_active(self) -> int:
			return self.connection.execute("SELECT COUNT(id) as count FROM Quests WHERE expires <= ?", (current_timestamp(),), fetch=1)

		def get_active(self, offset: int = 0, size: int = 10) -> list:
			quests = self.connection.execute("SELECT * FROM Quests WHERE expires <= ? ORDER BY expires ASC LIMIT ? OFFSET ?", (current_timestamp(), size, offset), fetch=True)
			results = []
			for quest in quests:
				results.append(Types.Quest(*quest))
			return results

		def get_expiring(self) -> list:
			quests = self.connection.execute("SELECT * FROM Quests WHERE expires <= ? ORDER BY expires ASC", (current_timestamp() - (60 * 60 * 24),), fetch=True)
			results = []
			for quest in quests:
				results.append(Types.Quest(*quest))
			return results

	class UserQuests(RelationTable):
		def __init__(self, connection):
			super().__init__(connection, name='UserQuests', attributes=('user', 'easy', 'normal', 'hard', 'insane', 'extra'))

		def create(self, user_id: int) -> None:
			self.connection.create(self.name, self.attributes, (user_id, 0, 0, 0, 0, 0))

		def get(self, user_id: int) -> tuple:
			return self.connection.get(self.name, user_id, key='user')
		
		# Custom
		def get_qp(self, user_id: int) -> int:
			try:
				return self.connection.execute("SELECT (easy * 1 + normal * 2 + hard * 3 + insane * 4 + extra * 5) FROM UserQuests WHERE user = ?", (user_id,), fetch=1)
			except:
				return 0
			
		def qp_rank(self, qp: int) -> int:
			try:
				return self.connection.execute("SELECT COUNT(user) FROM UserQuests WHERE easy * 1 + normal * 2 + hard * 3 + insane * 4 + extra * 5 >= ?", (qp,), fetch=1)
			except:
				return 0
		
		def qp_ranking(self, offset: int = 0, size: int = 10) -> list:
			return self.connection.execute("SELECT user, (easy * 1 + normal * 2 + hard * 3 + insane * 4 + extra * 5) AS points FROM UserQuests ORDER BY points DESC LIMIT ? OFFSET ?", (size, offset), fetch=True)
