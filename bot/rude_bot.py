import discord

from discord.ext import commands

from bot.greeting_manager import GreetingManager

class RudeBot:
	def __init__(self, token, handler, level, command_prefix="!"):
		intents = discord.Intents.default()
		intents.presences = True
		intents.message_content = True
		intents.voice_states = True
		intents.members = True
		self.bot = commands.Bot(command_prefix=command_prefix, intents=intents, help_command=None)
		self.token = token
		self.handler = handler
		self.level = level

		self.greetingManager = GreetingManager()

		self.register_events()
		self.register_commands()

	def register_events(self):
		@self.bot.event
		async def on_ready():
			print(f"Logged in as {self.bot.user.name} with ID {self.bot.user.id}")

		@self.bot.event
		async def on_voice_state_update(member, before, after):
			# Check if user joined a voice channel
			if before.channel is None and after.channel is not None:

				# Ignore bots
				if member.bot:
					return

				text_channel_id = 243539125632892928
				text_channel = member.guild.get_channel(text_channel_id)

				if not text_channel:
					return

				# Build and send the greeting
				greeting = self.greetingManager.get_random_join_greeting()

				text = greeting.get("text", "")
				emote = greeting.get("emote", "")
				gif_url = greeting.get("gif_url")

				parts = [member.mention]
				if text:
					parts.append(text)
				if emote:
					parts.append(emote)

				message = " ".join(parts)

				await text_channel.send(message)

				if gif_url:
					embed = discord.Embed()
					embed.set_image(url=gif_url)
					await text_channel.send(embed=embed)

	def register_commands(self):
		@self.bot.command(name="help", help="Good lord do i have to explain this one???")
		async def help_command(ctx):
			commands_list = []
			for command in self.bot.commands:
				# Skip hidden or internal commands if needed
				if not command.hidden:
					commands_list.append(f"**!{command.name}** - {command.help or 'No description'}")

			help_message = "I'm helping you against my better judgement...\n" + "\n".join(commands_list)
			await ctx.send(help_message)

		@self.bot.command(name="joke", help="This is for people with a sense of humor, so not you.")
		async def joke(ctx):
			await ctx.send("Your mother.")

		@self.bot.command(name="hello", help="I would rather you didn't say hello.")
		async def hello(ctx):
			greeting = self.greetingManager.get_random_message_greeting()

			# Safely get text, emote, and gif_url with defaults
			text = greeting.get("text", "")
			emote = greeting.get("emote", "")
			gif_url = greeting.get("gif_url")

			# Build the message parts, avoid extra spaces if emote missing
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

			# If gif_url is a non-empty string, send it as an embed
			if gif_url:
				embed = discord.Embed()
				embed.set_image(url=gif_url)
				await ctx.send(embed=embed)

	def run(self):
		self.bot.run(self.token, log_handler=self.handler, log_level=self.level)