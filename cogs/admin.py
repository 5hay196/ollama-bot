"""
Admin cog -- model management, health checks, bot statistics.
Admin access is controlled by the ADMIN_HASHES env variable.
"""

import os
import requests
from lxmfy import Cog, command

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


class AdminCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_admin(self, ctx) -> bool:
        return ctx.sender in self.bot.admins

    @command(name="setmodel", threaded=True)
    def setmodel(self, ctx, *, model: str):
        """[Admin] Switch the active Ollama model for all users."""
        if not self._is_admin(ctx):
            ctx.reply("Permission denied. This command requires admin access.")
            return
        self.bot.storage.set("current_model", model)
        ctx.reply(f"Active model switched to: {model}")

    @command(name="models", threaded=True)
    def models(self, ctx):
        """[Admin] List all models available on the Ollama instance."""
        if not self._is_admin(ctx):
            ctx.reply("Permission denied. This command requires admin access.")
            return
        try:
            res = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
            res.raise_for_status()
            model_list = res.json().get("models", [])
            if model_list:
                names = "\n".join(f"  - {m['name']}" for m in model_list)
                ctx.reply(f"Available models:\n{names}")
            else:
                ctx.reply("No models found. Pull one with: ollama pull llama3.2")
        except requests.exceptions.ConnectionError:
            ctx.reply(f"Error: Cannot reach Ollama at {OLLAMA_URL}")
        except Exception as e:
            ctx.reply(f"Error fetching models: {str(e)}")

    @command(name="status", threaded=True)
    def status(self, ctx):
        """[Admin] Check bot and Ollama service health."""
        if not self._is_admin(ctx):
            ctx.reply("Permission denied. This command requires admin access.")
            return

        current_model = self.bot.storage.get("current_model", DEFAULT_MODEL)

        try:
            requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            ollama_status = "online"
        except Exception:
            ollama_status = "offline"

        ctx.reply(
            f"Status report:\n"
            f"  Bot:          online\n"
            f"  Ollama:       {ollama_status}\n"
            f"  Ollama URL:   {OLLAMA_URL}\n"
            f"  Active model: {current_model}"
        )

    @command(name="clearall")
    def clearall(self, ctx):
        """[Admin] Instructions for wiping all user conversation history."""
        if not self._is_admin(ctx):
            ctx.reply("Permission denied. This command requires admin access.")
            return
        ctx.reply(
            "To wipe all user history: stop the bot, delete the bot_data/ directory, "
            "then restart."
        )


def setup(bot):
    bot.add_cog(AdminCog(bot))
