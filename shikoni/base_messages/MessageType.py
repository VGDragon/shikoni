import sys
from typing import BinaryIO

class MessageType:
    def __init__(self, type_id: int = -1):
        self._header = "shikoni"
        self.type_id = type_id

    def set_type_id(self, type_id: int):
        self.type_id = type_id
        return self

    def decode_io(self, file_io: BinaryIO):
        header = file_io.read(7).decode()
        if header != self._header:
            self.type_id = -1
            return self
        type_length = int.from_bytes(file_io.read(1), "big")
        self.type_id = int.from_bytes(file_io.read(type_length), "big")
        return self

    def decode_bytes(self, message_bytes: bytearray):
        if message_bytes[:7].decode() != self._header:
            self.type_id = -1
            return self
        del message_bytes[:7]
        type_length = message_bytes[0]
        del message_bytes[0]
        self.type_id = int.from_bytes(message_bytes[:type_length], "big")
        del message_bytes[:type_length]
        return self

    def encode(self):
        type_bytes = bytearray(self.type_id.to_bytes(sys.getsizeof(self.type_id), "big"))
        type_bytes = type_bytes.lstrip(bytes([0]))
        message_bytes = bytes([len(type_bytes)])
        return self._header.encode("utf-8") + message_bytes + type_bytes
