from typing import BinaryIO

from message_types.MessageType import MessageType

class ShikoniMessage:

    def __init__(self, message=None, message_type: MessageType = None):
        self.message = message
        if message_type is None:
            self.message_type = MessageType()
        else:
            self.message_type = message_type

    def decode_io(self, file_io: BinaryIO):
        message_bytes_length = int.from_bytes(file_io.read(1), "big")
        message_length = int.from_bytes(file_io.read(message_bytes_length), "big")
        return message_length

    def decode_bytes(self, message_bytes: bytearray):
        message_count_length = message_bytes[0]
        del message_bytes[0]

        message_length = int.from_bytes(message_bytes[:message_count_length], "big")
        del message_bytes[:message_count_length]
        return message_length

    def encode(self, message_bytes=b""):
        message_length = bytes([len(message_bytes)])
        return self.message_type.encode() + bytes([len(message_length)]) + message_length + message_bytes

