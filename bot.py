#!/usr/bin/env python3
"""
ollama-bot -- Private AI assistant over Reticulum mesh network.
Built with LXMFy + Ollama. Part of the reticulum-pi-mesh project.
https://github.com/5hay196/reticulum-pi-mesh
"""

import os
from dotenv import load_dotenv
from lxmfy import LXMFBot

load_dotenv()

bot = LXMFBot(
    name=os.getenv("BOT_NAME", "ITD5 AI Assistant"),
    announce=int(os.getenv("ANNOUNCE_INTERVAL", "600")),
    admins=[h.strip() for h in os.getenv("ADMIN_HASHES", "").split(",") if h.strip()],
    hot_reloading=True,
    rate_limit=int(os.getenv("RATE_LIMIT", "3")),
    cooldown=int(os.getenv("COOLDOWN", "60")),
    max_warnings=3,
    warning_timeout=300,
    storage_type="sqlite",
    storage_path="bot_data",
)

bot.load_cog("cogs.ai")
bot.load_cog("cogs.admin")

if __name__ == "__main__":
    bot.run()
