from discord.ext import commands

class EventHandler(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Logged in as {self.bot.user.name} with ID {self.bot.user.id}")

	@commands.Cog.listener()
	async def on_voice_state_update(self):
		"""
		Triggers when a voice state changes.
		Sends a random join greeting when a non-cogs member newly joins any voice channel.

		Parameters:
			member (discord.Member): Discord member object
		"""
		"""# Check if user joined a voice channel
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
				await text_channel.send(embed=embed)"""

async def setup(bot):
	await bot.add_cog(EventHandler(bot))