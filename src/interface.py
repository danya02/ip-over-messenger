from pytun import TunTapDevice
from .messenger import Channel
import asyncio

class NetworkInterface:
    """
    Class which holds the TUN interface and connects it to the messenger backend.
    """

    def __init__(self, channel: Channel, name: str='msg_tun', persist: bool=True):
        """
        channel is a fully-initialized Channel with a running receive loop.

        name is the name of the interface to create/connect to.

        persist is whether this interface should exist when the program is not running.
        """

        self.channel = channel

        self.device = TunTapDevice(name=name)
        self.device.persist(persist)
        self.device.mtu = self.channel.MAX_MTU()

        # TODO: make these configurable
        self.device.addr = '12.34.56.1'
        self.device.dstaddr = '12.34.56.2'
        self.device.netmask = '255.255.255.0'

        self.device.up()

        self.opened = True


        d2c = asyncio.create_task(self.device_to_channel_loop())
        c2d = asyncio.create_task(self.channel_to_device_loop())

        self.bidirectional_comms = asyncio.gather(d2c, c2d)


    async def write_to_device(self, data):
        print('Writing to interface', data)
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, self.device.write, data)
        return resp
    
    async def read_from_device(self):
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, self.device.read, self.device.mtu)
        return resp


    async def device_to_channel_loop(self):
        while self.opened:
            data_from_device = await self.read_from_device()
            await self.channel.send(data_from_device)

    async def channel_to_device_loop(self):
        while self.opened:
            data_from_channel = await self.channel.recv()
            await self.write_to_device(data_from_channel)

