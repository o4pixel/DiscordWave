"""
DiscordWave - A modern Python library for Discord bot development

A lightweight, asynchronous wrapper for the Discord API that makes
bot development intuitive and straightforward.
"""
import aiohttp
import asyncio
import json
import logging
import websockets
from typing import Callable, Dict, List, Optional, Union, Any

__version__ = "0.1.0"
__all__ = ["Client", "Intents", "Message", "User", "Command"]

class Intents:
    """Class representing Discord Gateway Intents"""
    
    def __init__(self, **kwargs):
        self.guilds = kwargs.get('guilds', False)
        self.members = kwargs.get('members', False)
        self.bans = kwargs.get('bans', False)
        self.emojis = kwargs.get('emojis', False)
        self.integrations = kwargs.get('integrations', False)
        self.webhooks = kwargs.get('webhooks', False)
        self.invites = kwargs.get('invites', False)
        self.voice_states = kwargs.get('voice_states', False)
        self.presences = kwargs.get('presences', False)
        self.messages = kwargs.get('messages', False)
        self.reactions = kwargs.get('reactions', False)
        self.typing = kwargs.get('typing', False)
        self.message_content = kwargs.get('message_content', False)
    
    @classmethod
    def default(cls):
        """Returns default intents with messages enabled"""
        return cls(messages=True)
    
    @classmethod
    def all(cls):
        """Returns all intents enabled"""
        return cls(
            guilds=True, members=True, bans=True, emojis=True,
            integrations=True, webhooks=True, invites=True,
            voice_states=True, presences=True, messages=True,
            reactions=True, typing=True, message_content=True
        )
    
    def to_integer(self) -> int:
        """Convert intents to integer for API"""
        value = 0
        if self.guilds: value |= (1 << 0)
        if self.members: value |= (1 << 1)
        if self.bans: value |= (1 << 2)
        if self.emojis: value |= (1 << 3)
        if self.integrations: value |= (1 << 4)
        if self.webhooks: value |= (1 << 5)
        if self.invites: value |= (1 << 6)
        if self.voice_states: value |= (1 << 7)
        if self.presences: value |= (1 << 8)
        if self.messages: value |= (1 << 9)
        if self.reactions: value |= (1 << 10)
        if self.typing: value |= (1 << 11)
        if self.message_content: value |= (1 << 15)
        return value

class Message:
    """Represents a Discord message"""
    
    def __init__(self, data: Dict[str, Any], client):
        self.id = data.get('id')
        self.channel_id = data.get('channel_id')
        self.guild_id = data.get('guild_id')
        self.author = User(data.get('author')) if data.get('author') else None
        self.content = data.get('content', '')
        self.timestamp = data.get('timestamp')
        self.client = client
    
    async def reply(self, content: str) -> 'Message':
        """Reply to this message"""
        return await self.client.send_message(
            self.channel_id, 
            content, 
            message_reference={"message_id": self.id}
        )

class User:
    """Represents a Discord user"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.username = data.get('username')
        self.discriminator = data.get('discriminator')
        self.avatar = data.get('avatar')
        self.bot = data.get('bot', False)

class Command:
    """Represents a bot command"""
    
    def __init__(self, name: str, callback: Callable, description: str = ""):
        self.name = name
        self.callback = callback
        self.description = description

class Client:
    """Main client for interacting with the Discord API"""
    
    API_VERSION = 10
    API_BASE = f"https://discord.com/api/v{API_VERSION}"
    GATEWAY_URL = f"{API_BASE}/gateway/bot"
    
    def __init__(self, token: str, intents: Intents = None):
        self.token = token
        self.intents = intents or Intents.default()
        self.session = None
        self.ws = None
        self.heartbeat_interval = None
        self.sequence = None
        self.session_id = None
        self.user = None
        self.commands = {}
        self.event_handlers = {
            "ready": [],
            "message_create": [],
            "guild_create": [],
        }
        self.logger = logging.getLogger('discordwave')
    
    def command(self, name: str = None, description: str = ""):
        """Decorator to register a command"""
        def decorator(func):
            command_name = name or func.__name__
            self.commands[command_name] = Command(command_name, func, description)
            return func
        return decorator
    
    def event(self, event_name: str = None):
        """Decorator to register an event handler"""
        def decorator(func):
            nonlocal event_name
            event_name = event_name or func.__name__
            self.event_handlers.setdefault(event_name, []).append(func)
            return func
        return decorator
    
    async def start(self):
        """Initialize and start the bot"""
        self.session = aiohttp.ClientSession()
        
        # Get gateway URL
        gateway_data = await self._api_request("GET", self.GATEWAY_URL)
        gateway_url = f"{gateway_data['url']}?v={self.API_VERSION}&encoding=json"
        
        # Connect to gateway
        self.logger.info(f"Connecting to gateway: {gateway_url}")
        self.ws = await websockets.connect(gateway_url)
        
        # Handle initial HELLO message
        hello_data = json.loads(await self.ws.recv())
        self.heartbeat_interval = hello_data['d']['heartbeat_interval'] / 1000
        
        # Start heartbeat loop
        asyncio.create_task(self._heartbeat_loop())
        
        # Identify with the gateway
        await self._identify()
        
        # Start event loop
        await self._event_loop()
    
    async def _heartbeat_loop(self):
        """Send heartbeats to keep the connection alive"""
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            await self.ws.send(json.dumps({
                "op": 1,  # Heartbeat opcode
                "d": self.sequence
            }))
            self.logger.debug("Heartbeat sent")
    
    async def _identify(self):
        """Send identify payload to Discord gateway"""
        identify_payload = {
            "op": 2,  # Identify opcode
            "d": {
                "token": self.token,
                "intents": self.intents.to_integer(),
                "properties": {
                    "$os": "linux",
                    "$browser": "discordwave",
                    "$device": "discordwave"
                }
            }
        }
        await self.ws.send(json.dumps(identify_payload))
    
    async def _event_loop(self):
        """Process events from the gateway"""
        async for message in self.ws:
            data = json.loads(message)
            self.sequence = data.get('s', self.sequence)
            
            if data['op'] == 0:  # Dispatch event
                event_name = data['t'].lower()
                event_data = data['d']
                
                if event_name == 'ready':
                    self.session_id = event_data['session_id']
                    self.user = User(event_data['user'])
                    self.logger.info(f"Logged in as {self.user.username}")
                
                elif event_name == 'message_create':
                    message = Message(event_data, self)
                    
                    # Check if the message is a command
                    if message.content.startswith('!'):
                        parts = message.content[1:].split(' ', 1)
                        command_name = parts[0]
                        if command_name in self.commands:
                            args = parts[1] if len(parts) > 1 else ""
                            await self.commands[command_name].callback(message, args)
                
                # Dispatch event to handlers
                for handler in self.event_handlers.get(event_name, []):
                    if event_name == 'message_create':
                        asyncio.create_task(handler(Message(event_data, self)))
                    else:
                        asyncio.create_task(handler(event_data))
    
    async def _api_request(self, method: str, url: str, **kwargs) -> Dict:
        """Make a request to the Discord API"""
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        
        if url.startswith('http'):
            full_url = url
        else:
            full_url = f"{self.API_BASE}{url}"
        
        async with self.session.request(method, full_url, headers=headers, **kwargs) as resp:
            return await resp.json()
    
    async def send_message(self, channel_id: str, content: str, **kwargs) -> Message:
        """Send a message to a channel"""
        payload = {"content": content, **kwargs}
        data = await self._api_request(
            "POST", 
            f"/channels/{channel_id}/messages", 
            json=payload
        )
        return Message(data, self)
    
    async def close(self):
        """Close the connection and cleanup"""
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()

    def run(self, token: str = None):
        """Run the bot (blocking)"""
        if token:
            self.token = token
            
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            loop.run_until_complete(self.close())
            self.logger.info("Bot has been shut down")
        finally:
            loop.close()
