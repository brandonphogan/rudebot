import discord

from discord.ext import commands

from bot.greeting_manager import GreetingManager

class RudeBot:
	"""
	Top level object to handle commands and events. Delegates logic to appropriate handlers.
	"""

	def __init__(self, token, text_channel_id, handler, log_level, command_prefix="!"):
		"""
		Initializes RudeBot.

		Parameters:
			self (RudeBot)
			token (string): Discord access token
			text_channel_id (int): Discord text channel ID
			handler (FileHandler): FileHandler to handle logging
			log_level (int): Logging level
			command_prefix (string): Command prefix to use
		"""
		intents = discord.Intents.default()
		intents.presences = True
		intents.message_content = True
		intents.voice_states = True
		intents.members = True
		self.bot = commands.Bot(command_prefix=command_prefix, intents=intents, help_command=None)
		self.token = token
		self.text_channel_id = text_channel_id
		self.handler = handler
		self.log_level = log_level

		self.greetingManager = GreetingManager()

		self.__register_events()
		self.__register_commands()

	def __register_events(self):
		"""
		Registers event handlers.

		Parameters:
			self (RudeBot)
		"""
		@self.bot.event
		async def on_ready():
			print(f"Logged in as {self.bot.user.name} with ID {self.bot.user.id}")

		@self.bot.event
		async def on_voice_state_update(member, before, after):
			"""
			Triggers when a voice state changes.
			Sends a random join greeting when a non-bot member newly joins any voice channel.

			Parameters:
				member (discord.Member): Discord member object
				before (discord.VoiceState): Voice state before
				after (discord.VoiceState): Voice state after
			"""
			# Check if user joined a voice channel
			if before.channel is None and after.channel is not None:

				# Ignore bots
				if member.bot:
					return

				# Get the text channel
				text_channel = member.guild.get_channel(self.text_channel_id)

				if not text_channel:
					return

				# TODO: Move greeting logic to greeting manager
				# Get random join greeting
				greeting = self.greetingManager.get_random_join_greeting()

				# Safely get text, emote, and gif_url with defaults
				text = greeting.get("text", "")
				emote = greeting.get("emote", "")
				gif_url = greeting.get("gif_url")

				# Append member mention and greeting parts
				parts = [member.mention]
				if text:
					parts.append(text)
				if emote:
					parts.append(emote)

				message = " ".join(parts)

				# Send the text + emote message if there is any text or emote
				await text_channel.send(message)

				# Send gif as separate message if applicable
				if gif_url:
					embed = discord.Embed()
					embed.set_image(url=gif_url)
					await text_channel.send(embed=embed)

	def __register_commands(self):
		"""
		Registers command handlers.

		Parameters:
			self (RudeBot)
		"""

		@self.bot.command(name="help", help="Good lord do i have to explain this one???")
		async def help_command(ctx):
			"""
			Displays list of commands and their usage (help text).

			Parameters:
				ctx (commands.Context): Discord context object
			"""
			commands_list = []
			for command in self.bot.commands:
				# Skip hidden or internal commands if needed
				if not command.hidden:
					commands_list.append(f"**!{command.name}** - {command.help or 'No description'}")

			help_message = "I'm helping you against my better judgement...\n" + "\n".join(commands_list)
			await ctx.send(help_message)

		@self.bot.command(name="joke", help="This is for people with a sense of humor, so not you.")
		async def joke(ctx):
			"""
			Displays a random joke.

			Parameters:
				ctx (commands.Context): Discord context object
			"""
			# TODO: Implement random jokes
			await ctx.send("Your mother.")

		@self.bot.command(name="hello", help="I would rather you didn't say hello.")
		async def hello(ctx):
			"""
			Displays a random message greeting.

			Parameters:
				ctx (commands.Context): Discord context object
			"""
			# TODO: Move greeting logic to greeting manager
			# Get random message greeting
			greeting = self.greetingManager.get_random_message_greeting()

			# Safely get text, emote, and gif_url with defaults
			text = greeting.get("text", "")
			emote = greeting.get("emote", "")
			gif_url = greeting.get("gif_url")

			# Append member mention and greeting parts
			message_parts = [ctx.author.mention]
			if text:
				message_parts.append(text)
			if emote:
				message_parts.append(emote)

			message_text = " ".join(message_parts)

			# Send the text + emote message if there is any text or emote
			if text or emote:
				await ctx.send(message_text)
			else:
				# If no text or emote, just mention the user
				await ctx.send(ctx.author.mention)

			# Send gif as separate message if applicable
			if gif_url:
				embed = discord.Embed()
				embed.set_image(url=gif_url)
				await ctx.send(embed=embed)

	def run(self):
		"""
		Runs the bot.

		Parameters:
			self (RudeBot)
		"""
		self.bot.run(self.token, log_handler=self.handler, log_level=self.log_level)