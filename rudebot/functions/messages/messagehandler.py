import discord
from discord.ext import commands
from functions.messages import responses


class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.bot:
            return

        if self.bot.user.mentioned_in(ctx):
            await interpret_message(ctx)


async def interpret_message(ctx):
    try:
        username = str(ctx.author.nick)
        channel = str(ctx.channel)
        user_message = str(ctx.content)
        user_message = user_message.split(" ", 1)[1] if len(
            user_message.split(" ", 1)) > 1 else ""

        print(f"{username} said: {user_message} ({channel})")

        # Private messages
        if len(user_message) and user_message[0] == '?':
            user_message = user_message[1:]
            response = responses.handle_response(
                user_message, username, is_private=True)
            await send_message(ctx, response, is_private=True)

        # Public messages
        else:
            response = responses.handle_response(user_message, username)

            # Shut em up
            if response == "I'm tired of listening to you." or response == "Congratulations, you get to see god today.":
                await ctx.author.move_to(None)

            if response == "Do you think you're funny?":
                if ctx.author.get_role(243542015743098880) == None:
                    await ctx.author.edit(nick="Silly dumb cunt")

            """ # Chinese fire drill lol
            if response == "Chinese fire drill!":
                server = client.guilds[0]
                print(server)
                voice_channels = [vc for vc in server.voice_channels]
                for voice_channel in voice_channels:
                    print(voice_channel)

                active_member_list = []
                for channel in voice_channel_list:
                    active_member_list = channel.members

                for member in active_member_list:
                    member.move_to(
                        voice_channel_list[random.randint(0, len(voice_channel_list))]) """

            await send_message(ctx, response)

    except Exception as e:
        print(e)


async def send_message(ctx, response, is_private=False):
    try:
        await ctx.author.send(response) if is_private else await ctx.channel.send(response)
    except Exception as e:
        print(e)


async def setup(bot):
    await bot.add_cog(MessageHandler(bot))
