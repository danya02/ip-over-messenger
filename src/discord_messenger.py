import discord
from discord.ext import tasks
from .messenger import Channel
import base65536
import asyncio
import threading
import logging
logging.basicConfig(level=logging.DEBUG)

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recv_packets = asyncio.Queue()

    async def on_connect(self):
        print('Connected')

    async def on_ready(self):
        print('Discord client ready')
        self.channel_obj = await self.fetch_channel(self.parent.channel)

    async def on_message(self, message):
        print(message)
        if message.channel.id == self.channel_obj.id:
            try:
                data = base65536.decode(message.content)
                print('Received data over Discord', data)
            except:
                print('Received garbage', repr(message.content))
                return
            await self.recv_packets.put(data)

    async def recv(self) -> bytes:
        return await self.recv_packets.get()

    async def send_data(self, data: bytes):    
        print('Sending over Discord', data)
        data = base65536.encode(data)
        await self.channel_obj.send(data)


class DiscordChannel(Channel):
    """
    Class that sends messages to a Discord text channel.
    It encodes binary data in Base65536.
    """

    @staticmethod
    def MAX_MTU() -> int:
        """
        Base65536 encodes every two bytes as a single character,
        and Discord allows 2000 characters by default,
        so the MTU is 4000 bytes.
        """
        return 4000


    def __init__(self, token: str, channel: int):
        """
        token is the Discord bot token.

        channel is the ID of a text channel that the bot has access to.
        """

        print('Start init DiscordChannel')

        self.token = token
        self.channel = channel
        self.queued_packets = []
        self.queued_packets_lock = threading.Lock()

        intents = discord.Intents.none()
        intents.messages = True
        self.client = MyClient(intents=intents)
        self.client.parent = self

        asyncio.create_task(self.client.start(self.token))


    async def send(self, data: bytes):
        await self.client.send_data(data)

    async def recv(self) -> bytes:
        return await self.client.recv()

