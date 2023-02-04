import discord
import responses


def run_bot():
    token = ''
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print("RudeBot is ruining your day!")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if client.user.mentioned_in(message):
            await interpret_message(message, client)

    client.run(token)


async def send_message(message, response, is_private=False):
    try:
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


async def interpret_message(message, client):
    try:
        username = str(message.author.nick)
        channel = str(message.channel)
        user_message = str(message.content)
        user_message = user_message.split(" ", 1)[1] if len(
            user_message.split(" ", 1)) > 1 else ""

        print(f"{username} said: {user_message} ({channel})")

        # Private messages
        if len(user_message) and user_message[0] == '?':
            user_message = user_message[1:]
            response = responses.handle_response(
                user_message, username, is_private=True)
            await send_message(message, response, is_private=True)

        # Public messages
        else:
            response = responses.handle_response(user_message, username)

            # Shut em up
            if response == "I'm tired of listening to you." or "Congratulations, you get to see god today.":
                await message.author.move_to(None)

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

            await send_message(message, response)

    except Exception as e:
        print(e)
