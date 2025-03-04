import asyncio
import logging
from discordwave import Client, Intents

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot with necessary intents
intents = Intents(messages=True, message_content=True, guilds=True)
bot = Client(token="YOUR_TOKEN_HERE", intents=intents)

# Event handler for when the bot is ready
@bot.event("ready")
async def on_ready(data):
    print(f"Bot is running as {bot.user.username}")
    print(f"Bot ID: {bot.user.id}")
    print("Connected to the following guilds:")
    
    # We'll set a custom status after connecting
    await asyncio.sleep(2)
    print("Status updated!")

# Event handler for new messages
@bot.event("message_create")
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author.id == bot.user.id:
        return
    
    # Log messages for demonstration
    print(f"Message from {message.author.username}: {message.content}")
    
    # Simple response example (not a command)
    if "hello bot" in message.content.lower():
        await message.reply("Hello there! Try using my commands with the ! prefix.")

# Basic ping command
@bot.command()
async def ping(message, args):
    """Simple ping command to check if the bot is responsive"""
    await message.reply("Pong! 🏓")

# Echo command that repeats what the user said
@bot.command(description="Repeats your message back to you")
async def echo(message, args):
    if not args:
        await message.reply("You didn't provide anything for me to echo!")
    else:
        await message.reply(f"Echo: {args}")

# Help command to list available commands
@bot.command(description="Shows the list of available commands")
async def help(message, args):
    commands_list = "\n".join([
        f"!{name} - {cmd.description}" 
        for name, cmd in bot.commands.items()
    ])
    
    await message.reply(f"**Available Commands:**\n{commands_list}")

# User info command
@bot.command(name="userinfo", description="Shows information about a user")
async def user_info(message, args):
    user = message.author
    response = f"**User Information**\n"
    response += f"Username: {user.username}\n"
    response += f"ID: {user.id}\n"
    
    await message.reply(response)

# Start the bot
if __name__ == "__main__":
    bot.run()  # You can also pass the token here: bot.run("YOUR_TOKEN_HERE")
