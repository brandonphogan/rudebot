from discord.ext import commands
from services.response_service import BotResponse, send_response, get_random_response, format_response_text
from services.action_service import handle_action
from utils.logging_util import get_logger

class Commands(commands.Cog):
    """
    Cog for handling text commands for the Discord bot.
    Includes custom help, hello, and joke commands.
    Uses services for response formatting, sending, and action handling.
    """
    def __init__(self, bot):
        self.bot = bot
        # Remove default help command to use custom help
        bot.help_command = None
        # Set up a dedicated logger for this cog
        self.logger = get_logger('commands', 'logs/commands.log')

    @commands.command(name="help", help="Good lord do i have to explain this one???")
    async def help(self, ctx, *, command_name=None):
        """
        Custom help command. Lists all commands or details for a specific command.
        """
        if command_name is None:
            # Show general help with all command names
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
        Responds to the user with a random 'hello' response from the database.
        May include text, an emote, a gif, or perform an action (kick/scatter).
        """
        # Fetch a random hello response from the database
        rand_response = get_random_response("command", "hello")
        if not rand_response:
            await ctx.send(f"{ctx.author.mention} I have nothing to say to you.")
            self.logger.info(f"No hello response found for {ctx.author} in channel {ctx.channel.id} (guild {ctx.guild.id})")
            return
        # Format the response text (mention + text + emote)
        formatted_text = format_response_text(ctx.author, rand_response.text or "", rand_response.emote or "")
        # Build the BotResponse dataclass
        bot_response = BotResponse(
            text=formatted_text,
            gif_url=rand_response.gif_url,
            action=rand_response.action
        )
        # Send the response and log the action
        await send_response(ctx, bot_response, logger=self.logger)
        # Handle any special actions (kick, scatter, etc.)
        await handle_action(rand_response.action, ctx, logger=self.logger)

    @commands.command(name="joke", help="This is for people with a sense of humor, so not you.")
    async def joke(self, ctx):
        """
        Placeholder joke command.
        """
        await ctx.send("Your mother.")

# Required setup function for loading the cog
async def setup(bot):
    await bot.add_cog(Commands(bot))
