from src.discord_messenger import DiscordChannel
from src.interface import NetworkInterface
import signal
import asyncio
import secrets

async def main():
    chan = DiscordChannel(secrets.token, secrets.channel)
    iface = NetworkInterface(chan)
    await iface.bidirectional_comms

asyncio.run(main())
