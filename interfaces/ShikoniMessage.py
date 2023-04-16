from typing import BinaryIO
import sys
from message_types.MessageType import MessageType

class ShikoniMessage:

    def __init__(self, message=None, message_type: MessageType = None, shikoni=None):
        self.message = message
        if message_type is None:
            self.message_type = MessageType()
        else:
            self.message_type = message_type
        self.shikoni = shikoni

    def decode_bytes_length(self, message_bytes: bytearray):
        length_length = message_bytes[0]
        del message_bytes[0]
        length = int.from_bytes(message_bytes[:length_length], "big")
        del message_bytes[:length_length]
        return length

    def decode_bytes_length_io(self, file_io: BinaryIO):
        length_length = int.from_bytes(file_io.read(1), "big")
        length = int.from_bytes(file_io.read(length_length), "big")
        return length

    def encode_bytes_length(self, length: int):
        length_bytes = bytearray(length.to_bytes(sys.getsizeof(length), "big"))
        length_bytes = length_bytes.lstrip(bytes([0]))
        length_length = bytearray([len(length_bytes)])
        return length_length + length_bytes

    def decode_io(self, file_io: BinaryIO):
        return self.decode_bytes_length_io(file_io)

    def decode_bytes(self, message_bytes: bytearray):
        return self.decode_bytes_length(message_bytes)

    def encode(self, message_bytes=b""):
        return self.message_type.encode() + self.encode_bytes_length(len(message_bytes)) + message_bytes

