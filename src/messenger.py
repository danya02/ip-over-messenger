from abc import ABC, abstractmethod
from typing import Callable

class Channel(ABC):
    """
    Abstract class representing a messenger channel.

    This represents some structure within a messenger application
    such that messages can be sent into it and others can get these.
    
    This class must handle things like authentication, a loop for receiving
    messages, and de/serialization of message contents to a form acceptable
    to the underlying messenger transport.
    """


    @abstractmethod
    @staticmethod
    @property
    def MAX_MTU() -> int:
        """
        Return the absolute maximum number of bytes that can be sent over this.

        This restriction arises from things like the maximum number of characters
        allowed in a message. If in doubt, it is better to set it lower than higher.
        """
        raise NotImplementedError

    @property
    def on_receive(self) -> Callable[[bytes], None]:
        """
        Callable which will be called when a packet has been received.
        """
        if '_on_recv' not in self.__dict__:
            return None
        else:
            return self._on_recv

    @on_receive.setter
    def set_on_receive(self, new_value: Callable[[bytes], None]):
        self._on_recv = new_value


    @abstractmethod
    def send(self, data: bytes) -> None:
        """
        Send an IP packet containing this data.

        Depending on the transport, this may mean creating a text message.
        """
        raise NotImplementedError

