import sys
from typing import BinaryIO

from interfaces.ShikoniMessage import ShikoniMessage
from message_types.MessageType import MessageType


class ShikoniMessageString(ShikoniMessage):

    def __init__(self, message=None, message_type: MessageType = None):
        super().__init__(message, message_type)
        self.message_type.type_id = 10  # String

    def decode_io(self, file_io: BinaryIO):
        message_length = super().decode_io(file_io)
        self.message = file_io.read(message_length).decode()

    def decode_bytes(self, message_bytes: bytearray):
        message_length = super().decode_bytes(message_bytes)

        self.message = message_bytes[:message_length].decode()
        del message_bytes[:message_length]

    def encode_message(self):
        return self.message.encode("utf-8")

    def encode(self, message_bytes=b""):
        return super().encode(self.encode_message())
