## WillyBot
A bot written using [discord.py](https://discordpy.readthedocs.io/en/stable/) for [my Discord server](https://discord.gg/willy). What is the purpose? I don't know... just to have a fun little bot for the community. This was originally created in 2018 to send random images of [Josh](https://osu.ppy.sh/users/3441616), but was remade and has been the primary bot on my server since 2022 (with a complete rewrite in August 2025!).

## Structure
The core idea is based around a central database, from which all data is represented and interacted with through commands. While some commands and functionality may not need the database, the primary function is to give the user a custom "profile" with accolades and statistics for their time in the server.

### Database
This is a brief overview of the tables in the database and their purpose, for all attributes or typing please check the schema in `core/database.py`'s `Connection.__build__()` method.
- **Users** - stores user information such as Discord `id`, custom `name`, `joined` and `active` timestamps, etc.
- **Badges** - stores badges (rewards for users) including identifiers and an `image` path, etc.
- **UserBadges** - referencing table, entries representing a badge that a user owns as a (user id, badge id) pair
- **Quests** - stores quests (challenges for server members) with a message `id`, `tier` of difficulty, `expires` timestamp, etc.
- **UserQuests** - referencing table, for each user id there are counts of each quest tier completed

### Files
- **bot.py** - the main for the bot
- **core/common.py** - for common constants and static functions shared between cogs
- **core/database.py** - implements database operations in a simple class-hierarchical structure
- **cogs/users.py** commands that interact with the `Users` table (i.e. custom profiles, level system)
- **cogs/badges.py** commands related to user awarded badges, (`Badges` and `UserBadges` tables)
- **cogs/quests.py** commands implementing member quests, (`Quests` and `UserQuests` tables)
- **cogs/fun.py** extra commands that serve no "practical" purpose
- **cogs/server.py** commands for roles management and moderation
- **cogs/tasks.py** holding all the task loops for database/temp cleanup and other repetitive needs

### What's next?
- [x] Major rewrite to move all direct database interaction into a separate file
- [x] "Open source" the bot so that server members can contribute
- [ ] Integration with other websites (Twitch, osu!, etc.)
