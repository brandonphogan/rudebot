"""
Console service for Rudebot.
Provides interactive console commands for bot management.
Separates console logic from main bot functionality.
"""
import asyncio
import threading
import logging
import sys
from typing import Optional


class ConsoleService:
    """
    Handles console input and command processing for the bot.
    Runs in a separate thread to avoid blocking the main event loop.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("console")
        self.running = False
        self.console_thread = None
        
    def start(self):
        """Start the console listener in a separate thread."""
        if self.running:
            return
            
        self.running = True
        
        # Create console tracking file
        try:
            with open('.console_running', 'w') as f:
                f.write('true')
        except Exception as e:
            self.logger.error(f"Could not create console tracking file: {e}")
            
        self.console_thread = threading.Thread(target=self._console_loop, daemon=True)
        self.console_thread.start()
        self.logger.info("Console interface started. Type 'help' for available commands.")
        
    def stop(self):
        """Stop the console listener."""
        self.running = False
        
        # Clean up tracking file
        try:
            import os
            if os.path.exists('.console_running'):
                os.remove('.console_running')
        except Exception as e:
            self.logger.error(f"Could not remove console tracking file: {e}")
        
    def _console_loop(self):
        """Main console input loop running in separate thread."""
        while self.running:
            try:
                command = input().strip().lower()
                if command:
                    # Schedule command execution in the main event loop
                    asyncio.run_coroutine_threadsafe(
                        self._handle_command(command), 
                        self.bot.loop
                    )
            except (EOFError, KeyboardInterrupt):
                # Handle Ctrl+C or EOF gracefully
                asyncio.run_coroutine_threadsafe(
                    self._handle_command("stop"), 
                    self.bot.loop
                )
                break
            except Exception as e:
                self.logger.error(f"Console error: {e}")
                
    async def _handle_command(self, command: str):
        """Process console commands."""
        parts = command.split()
        cmd = parts[0] if parts else ""
        
        match cmd:
            case "help" | "h":
                self._show_help()
                
            case "stop" | "quit" | "exit":
                self.logger.info("Stopping bot via console command...")
                await self._stop_bot()
                
            case "restart":
                self.logger.info("Restarting bot via console command...")
                await self._restart_bot()
                
            case "status" | "info":
                await self._show_status()
                
            case "guilds":
                await self._show_guilds()
                
            case "reload":
                if len(parts) > 1:
                    await self._reload_cog(parts[1])
                else:
                    self.logger.info("Usage: reload <cog_name>")
                    loaded_cogs = list(self.bot.extensions.keys())
                    if loaded_cogs:
                        cog_list = ', '.join([cog.replace('cogs.', '') for cog in loaded_cogs])
                        self.logger.info(f"Available cogs: {cog_list}")
                        
            case "cogs" | "list":
                await self._list_cogs()
                    
            case "":
                pass  # Empty command, ignore
                
            case _:
                self.logger.warning(f"Unknown command: {command}. Type 'help' for available commands.")
                
    def _show_help(self):
        """Display available console commands."""
        help_text = """
Available Console Commands:
  help, h          - Show this help message
  stop, quit, exit - Gracefully stop the bot
  restart          - Restart the bot (requires external script)
  status, info     - Show bot status and statistics
  guilds           - List connected guilds
  cogs, list       - List all loaded cogs
  reload <cog>     - Reload a specific cog
        """.strip()
        
        print(help_text)
        
    async def _stop_bot(self):
        """Gracefully stop the bot."""
        self.stop()  # Stop console listener
        await self.bot.close()
        
    async def _restart_bot(self):
        """Restart the bot (requires external script to handle restart)."""
        self.logger.info("Bot restart requested. Shutting down...")
        # Create a restart flag file that external scripts can detect
        try:
            with open('.restart_requested', 'w') as f:
                f.write('restart')
        except Exception as e:
            self.logger.error(f"Could not create restart flag: {e}")
        
        await self._stop_bot()
        
    async def _show_status(self):
        """Display bot status information."""
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count for guild in self.bot.guilds)
        
        status_info = f"""
Bot Status:
  Connected: {not self.bot.is_closed()}
  Latency: {self.bot.latency * 1000:.1f}ms
  Guilds: {guild_count}
  Users: {user_count}
  Loaded Cogs: {len(self.bot.cogs)}
        """.strip()
        
        self.logger.info(status_info)
        
    async def _show_guilds(self):
        """Display connected guilds."""
        if not self.bot.guilds:
            self.logger.info("Not connected to any guilds.")
            return
            
        self.logger.info("Connected Guilds:")
        for guild in self.bot.guilds:
            self.logger.info(f"  {guild.name} (ID: {guild.id}, Members: {guild.member_count})")
            
    async def _reload_cog(self, cog_name: str):
        """Reload a specific cog."""
        try:
            # If user provided short name, try to find matching cog
            if not cog_name.startswith("cogs."):
                # Check if it's a partial match
                loaded_cogs = list(self.bot.extensions.keys())
                matches = [cog for cog in loaded_cogs if cog_name in cog]
                
                if len(matches) == 1:
                    full_cog_name = matches[0]
                elif len(matches) > 1:
                    self.logger.error(f"Ambiguous cog name '{cog_name}'. Matches: {', '.join(matches)}")
                    return
                else:
                    full_cog_name = f"cogs.{cog_name}"
            else:
                full_cog_name = cog_name
                
            await self.bot.reload_extension(full_cog_name)
            self.logger.info(f"Successfully reloaded cog: {full_cog_name}")
        except Exception as e:
            self.logger.error(f"Failed to reload cog '{cog_name}': {e}")
            # Show available cogs for reference
            loaded_cogs = list(self.bot.extensions.keys())
            if loaded_cogs:
                cog_list = ', '.join([cog.replace('cogs.', '') for cog in loaded_cogs])
                self.logger.info(f"Available cogs: {cog_list}")
                
    async def _list_cogs(self):
        """Display all loaded cogs."""
        loaded_cogs = list(self.bot.extensions.keys())
        if not loaded_cogs:
            self.logger.info("No cogs loaded.")
            return
            
        self.logger.info("Loaded Cogs:")
        for cog in loaded_cogs:
            cog_name = cog.replace('cogs.', '')
            self.logger.info(f"  {cog_name} ({cog})")