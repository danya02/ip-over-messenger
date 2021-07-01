from pytun import TunTapDevice
from .messenger import Channel
import threading

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
        channel.on_receive = self.receive

        self.device = TunTapDevice(name=name)
        self.device.persist(persist)
        self.device.mtu = self.channel.MAX_MTU

        # TODO: make these configurable
        self.device.addr = '12.34.56.1'
        self.device.dstaddr = '12.34.56.2'
        self.device.netmask = '255.255.255.0'

        self.opened = True
        self.dev_channel_thread = threading.Thread(target=self.device_to_channel_loop, daemon=True)
        self.dev_channel_thread.start()


    def device_to_channel_loop(self):
        """
        Loop that reads data from the interface and sends it to the channel.
        """
        while self.opened:
            data = self.device.read(self.device.mtu)
            self.channel.send(data)


    def receive(self, data: bytes) -> None:
        """
        Send the data that arrived via channel to the interface.
        """
        self.device.write(data)


