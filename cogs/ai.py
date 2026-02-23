"""
AI cog -- handles Ollama LLM queries with per-user conversation history.
"""

import os
import json
import requests
from lxmfy import Cog, command

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful AI assistant accessible over a Reticulum mesh network. "
    "Keep responses concise and clear. Avoid unnecessary formatting -- plain text works best "
    "over mesh links."
)
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "10"))


class AICog(Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_history(self, user_hash: str) -> list:
        """Retrieve conversation history for a user from storage."""
        raw = self.bot.storage.get(f"history_{user_hash}", "[]")
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

    def _save_history(self, user_hash: str, history: list):
        """Persist conversation history, trimming to MAX_HISTORY turns."""
        # Each turn = 2 messages (user + assistant), so keep last MAX_HISTORY * 2 messages
        trimmed = history[-(MAX_HISTORY * 2):]
        self.bot.storage.set(f"history_{user_hash}", json.dumps(trimmed))

    def _get_active_model(self) -> str:
        """Get the currently active model from storage, falling back to default."""
        return self.bot.storage.get("current_model", DEFAULT_MODEL)

    @command(name="ask", threaded=True)
    def ask(self, ctx, *, prompt: str):
        """Ask the AI a question. Maintains conversation history per user."""
        history = self._get_history(ctx.sender)
        history.append({"role": "user", "content": prompt})

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        model = self._get_active_model()

        try:
            res = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": model, "messages": messages, "stream": False},
                timeout=120,
            )
            res.raise_for_status()
            reply = res.json()["message"]["content"]
            history.append({"role": "assistant", "content": reply})
            self._save_history(ctx.sender, history)
            ctx.reply(reply)
        except requests.exceptions.Timeout:
            ctx.reply(
                "Error: Ollama timed out. The model may still be loading -- "
                "please wait a moment and try again."
            )
        except requests.exceptions.ConnectionError:
            ctx.reply(
                "Error: Cannot reach Ollama. "
                f"Is it running at {OLLAMA_URL}?"
            )
        except Exception as e:
            ctx.reply(f"Error: {str(e)}")

    @command(name="clear")
    def clear(self, ctx):
        """Clear your conversation history with the bot."""
        self.bot.storage.set(f"history_{ctx.sender}", "[]")
        ctx.reply("Conversation history cleared.")

    @command(name="model")
    def model(self, ctx):
        """Show the currently active LLM model."""
        model = self._get_active_model()
        ctx.reply(f"Active model: {model}")

    @command(name="help")
    def help(self, ctx):
        """Show available commands."""
        ctx.reply(
            "Commands:\n"
            "  /ask <question>  - Ask the AI\n"
            "  /clear           - Clear conversation history\n"
            "  /model           - Show active model\n"
            "  /help            - Show this message"
        )


def setup(bot):
    bot.add_cog(AICog(bot))
