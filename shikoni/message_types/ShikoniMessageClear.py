from typing import BinaryIO

from shikoni.interfaces.ShikoniMessage import ShikoniMessage
from shikoni.base_messages.MessageType import MessageType


class ShikoniMessageClear(ShikoniMessage):

    def __init__(self, message=None, message_type: MessageType = None, shikoni=None):
        super().__init__(message, message_type, shikoni)
        self.message_type.type_id = 103  # Clear

    def decode_io(self, file_io: BinaryIO):
        super().decode_io(file_io)

    def decode_bytes(self, message_bytes: bytearray):
        super().decode_bytes(message_bytes)

    def encode(self, message_bytes=b""):
        return super().encode()
