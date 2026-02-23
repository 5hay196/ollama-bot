# ollama-bot

A private AI assistant accessible over a [Reticulum](https://reticulum.network) mesh network. Built with [LXMFy](https://lxmfy.quad4.io/) and [Ollama](https://ollama.com) — run local LLMs on a Raspberry Pi and access them from any device on your mesh (Sideband, reticulum-meshchat) with zero internet dependency.

```
[Sideband on phone / reticulum-meshchat in browser]
         | LXMF messages (encrypted, signed)
[Reticulum -- LAN, WiFi, or LoRa]
         |
[Raspberry Pi / Server Node]
  +-- rnsd (Reticulum daemon)
  +-- ollama-bot (this project)
  +-- ollama serve
        +-- llama3.2 / mistral / phi3 / ...
```

## Features

- **Multi-turn conversations** -- per-user conversation history via SQLite
- **Model switching** -- admin can change the active LLM at runtime
- **Rate limiting** -- built-in per-user cooldowns and spam protection
- **Offline-first** -- zero cloud dependencies, all inference runs locally
- **Threaded LLM calls** -- non-blocking, bot remains responsive during inference
- **Signed messages** -- Ed25519 cryptographic signing via RNS identities
- **Systemd service** -- runs as a background service on the Pi

## Requirements

- Python 3.11+
- [Reticulum Network Stack](https://github.com/markqvist/Reticulum)
- [Ollama](https://ollama.com) running locally or an LAN
- Raspberry Pi 4 (4GB) for 3B models, Pi 5 recommended for 7B+

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/5hay196/ollama-bot
cd ollama-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# 4. Configure the bot
cp config.example.env .env
# Edit .env -- set ADMIN_HASHES to your RNS identity hash

# 5. Run the bot
python bot.py
```

## Commands

| Command | Description | Access |
|---|---|---|
| `/ask <question>` | Ask the AI (maintains conversation history) | All users |
| `/clear` | Clear your conversation history | All users |
| `/model` | Show the currently active model | All users |
| `/help` | Show available commands | All users |
| `/setmodel <name>` | Switch the active Ollama model | Admin only |
| `/models` | List models available on Ollama | Admin only |
| `/status` | Check bot and Ollama health | Admin only |

## Configuration

Copy `config.example.env` to `.env` and configure:

| Variable | Default | Description |
|---|---|---|
| `BOT_NAME` | `ITD5 AI Assistant` | Bot display name announced on mesh |
| `ADMIN_HASHES` | _(empty)_ | Comma-separated RNS identity hashes for admins |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API base URL |
| `OLLAMA_MODEL` | `llama3.2` | Default model to use |
| `SYSTEM_PROMPT` | _(see config)_ | System prompt for the LLM |
| `MAX_HISTORY` | `10` | Number of conversation turns to keep per user |
| `ANNOUNCE_INTERVAL` | `600` | Seconds between mesh announcements |
| `RATE_LIMIT` | `3` | Max requests per user per cooldown period |
| `COOLDOWN` | `60` | Cooldown window in seconds |

## Hardware Notes

- **Raspberry Pi 4 (4GB):** Suitable for 3B parameter models (llama3.2:3b, phi3:mini). Inference: 30-120s.
- **Raspberry Pi 5 (8GB):** Recommended for 7B parameter models. Inference: 10-30s.
- **LoRa:** For true off-grid use, add an [RNode](https://unsigned.io/rnode/) or compatible LoRa HAT. Keep system prompts short -- LoRa bandwidth is ~1-5 kbps.

## Part of the reticulum-pi-mesh Project

This bot is part of the broader [reticulum-pi-mesh](https://github.com/5hay196/reticulum-pi-mesh) project -- exploring LoRa mesh networking and AI integration on Raspberry Pi.

## License

MIT
