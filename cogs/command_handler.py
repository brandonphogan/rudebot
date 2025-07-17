import discord
from discord.ext import commands

import json
import random

from utils.path_helper import get_data_file

class CommandHandler(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		bot.help_command = None
		self.command_responses = {}
		self.__load_command_responses()

	def __load_command_responses(self):
		"""
		Loads command responses from file.
		"""
		try:
			with open(get_data_file("command_responses.json"), "r", encoding="utf-8") as f:
				self.command_responses = json.load(f)
		except Exception as e:
			print(f"[CommandHandler] Failed to load command responses: {e}")
			self.command_responses = {}

	def __get_responses_by_type(self, response_type):
		return [r for r in self.command_responses if r.get("command_type") == response_type]

	def __build_safe_response(self, ctx, response_type):
		response_parts = {"text": "", "gif_url": "", "action": ""}
		responses = self.__get_responses_by_type(response_type)
		rand_response = random.choice(responses)

		if rand_response:
			# Safely get text, emote, gif_url, and action with defaults
			text = rand_response.get("text", "")
			emote = rand_response.get("emote", "")
			gif_url = rand_response.get("gif_url", "")
			action = rand_response.get("action", "")

			# Concat member mention, text, and emote parts
			response_parts = {"text": ctx.author.mention}
			if text:
				response_parts["text"] += f" {text}"
			if emote:
				response_parts["text"] += f" {emote}"

			# Add gif_url and action
			if gif_url:
				response_parts["gif_url"] = gif_url
			if action:
				response_parts["action"] = action
		else:
			response_parts["text"] = f"{ctx.author.mention} I have nothing to say to you."

		return response_parts

	@commands.command(name="help", help="Good lord do i have to explain this one???")
	async def help(self, ctx, *, command_name=None):
		if command_name is None:
			# Show general help
			cmds = [command.name for command in self.bot.commands if not command.hidden]
			cmds_list = ", ".join(cmds)
			await ctx.send(f"I'm helping you against my better judgement...\n"
						   f"{cmds_list}\n"
						   f"Use `!help <command>` for more info or whatever.")
		else:
			# Show help for a specific command
			command = self.bot.get_command(command_name)
			if command:
				await ctx.send(f"**{command.name}**: {command.help or 'No description provided.'}")
			else:
				await ctx.send(f"No command named `{command_name}` found.")

	@commands.command(name="hello", help="I would rather you didn't say hello.")
	async def hello(self, ctx):
		"""
		Returns a random response from command_responses.json.

		Parameters:
			self (CommandHandler)
			ctx (commands.Context): Discord context object
		"""
		# Get random response
		safe_hello_response = self.__build_safe_response(ctx, "hello")

		# Send the text portion of the response
		if safe_hello_response.get("text"):
			await ctx.send(safe_hello_response.get("text"))

		# Send the gif
		if safe_hello_response.get("gif_url"):
			embed = discord.Embed()
			embed.set_image(url=safe_hello_response.get("gif_url"))
			await ctx.send(embed=embed)

		# Perform the action
		if safe_hello_response.get("action"):
			match safe_hello_response.get("action").lower():
				case "kick":
					if ctx.author.voice and ctx.author.voice.channel:
						await ctx.author.move_to(None, reason=None)
				case "scatter":
					# Get the voice channel of the command author
					current_vc = ctx.author.voice.channel if ctx.author.voice else None
					if current_vc:
						# Get all other voice channels excluding current
						other_vcs = [vc for vc in ctx.guild.voice_channels if vc != current_vc]
						if other_vcs:
							members = current_vc.members
							if members:
								# Shuffle and assign each member to a random other voice channel
								for member in members:
									target_vc = random.choice(other_vcs)
									await member.move_to(target_vc)

	@commands.command(name="joke", help="This is for people with a sense of humor, so not you.")
	async def joke(self, ctx):
		"""
		Displays a random joke.

		Parameters:
			ctx (commands.Context): Discord context object
		"""
		# TODO: Implement random jokes
		await ctx.send("Your mother.")

async def setup(bot):
	await bot.add_cog(CommandHandler(bot))
