import sys
from typing import BinaryIO

from interfaces.ShikoniMessage import ShikoniMessage
from message_types.MessageType import MessageType


class ShikoniMessageConnectClient(ShikoniMessage):

    def __init__(self, message=None, message_type: MessageType = None):
        super().__init__(message, message_type)
        self.message_type.type_id = 1  # Connect Client
        # message: tuple
        # 0: port
        # 1: url

    def decode_io(self, file_io: BinaryIO):
        message_length = super().decode_io(file_io)

        port_length = int.from_bytes(file_io.read(1), "big")
        port = int.from_bytes(file_io.read(port_length), "big")
        url = file_io.read(message_length - (1 + port_length)).decode()

        self.message = (port, url)

    def decode_bytes(self, message_bytes: bytearray):
        message_length = super().decode_bytes(message_bytes)
        port_length = message_bytes[0]
        del message_bytes[0]

        port = int.from_bytes(message_bytes[:port_length], "big")
        del message_bytes[:port_length]

        url = message_bytes[:message_length - (1 + port_length)].decode()
        del message_bytes[:message_length]
        self.message = (port, url)

    def encode_message(self):
        port_bytes = bytearray(self.message[0].to_bytes(sys.getsizeof(self.message[0]), "big"))

        port_bytes = port_bytes.lstrip(bytes([0]))
        port_length = bytes([len(port_bytes)])

        return port_length + port_bytes + self.message[1].encode("utf-8")

    def encode(self, message_bytes=b""):
        return super().encode(self.encode_message())
