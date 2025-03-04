# DiscordWave

A modern, lightweight Python library for building Discord bots with ease.

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![License MIT](https://img.shields.io/badge/license-MIT-green.svg)

## Overview

DiscordWave is an asynchronous Python library that provides a clean, intuitive interface to the Discord API. It's designed to be easy to use while still offering powerful features for creating Discord bots.

## Features

- 🚀 **Simple and intuitive**: Clean API design with sensible defaults
- ⚡ **Fully asynchronous**: Built with `asyncio` for high performance
- 🛠️ **Command framework**: Easy to create and manage commands
- 🔧 **Event-driven architecture**: Register handlers for Discord events
- 🧩 **Minimal dependencies**: Only requires a few external packages

## Installation

### Install from GitHub (Recommended)

```bash
pip install git+https://github.com/o4pixel/discordwave.git
```


### Install from source

```bash
git clone https://github.com/o4pixel/discordwave.git
cd discordwave
pip install .
```

## Quick Start

Here's a simple example of a bot that responds to a "!ping" command:

```python
from discordwave import Client, Intents

# Initialize with required intents
bot = Client(token="YOUR_TOKEN_HERE", intents=Intents.default())

@bot.command()
async def ping(message, args):
    """Simple ping command"""
    await message.reply("Pong! 🏓")

# Start the bot
bot.run()
```

## Creating a Bot

1. Create an application in the [Discord Developer Portal](https://discord.com/developers/applications)
2. Add a bot to your application
3. Copy your bot token
4. Invite the bot to your server using the OAuth2 URL generator (with messages and bot permissions)
5. Run your bot with the token

## Documentation

### Client

The main interface to Discord:

```python
client = Client(token="YOUR_TOKEN_HERE", intents=Intents.default())
```

### Intents

Control which events your bot receives:

```python
# Only receive message events
intents = Intents(messages=True, message_content=True)

# Receive all events (requires privileged intents)
intents = Intents.all()
```

### Commands

Register commands easily with decorators:

```python
@bot.command(name="greet", description="Greets a user")
async def greet_command(message, args):
    await message.reply(f"Hello, {message.author.username}!")
```

### Events

Listen for Discord events:

```python
@bot.event("guild_create")
async def on_guild_join(guild_data):
    print(f"Bot added to a new guild: {guild_data['name']}")
```

## Example Bot

Check out `examplebot.py` in the repository for a working example bot with several commands.

## Requirements

- Python 3.8 or higher
- aiohttp 3.7.4 or higher
- websockets 10.0 or higher

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
