import sys
from typing import BinaryIO

from interfaces.ShikoniMessage import ShikoniMessage
from base_messages.MessageType import MessageType


class ShikoniMessageConnectorName(ShikoniMessage):

    def __init__(self, message=None, message_type: MessageType = None, shikoni=None):
        super().__init__(message, message_type, shikoni)
        self.message_type.type_id = 4  # Connector names
        self.is_server = True
        self.connection_name: str = ""

    def set_variables(self, is_server: bool, connection_name: str):
        self.is_server = is_server
        self.connection_name: str = connection_name
        return self

    def decode_io(self, file_io: BinaryIO):
        message_length = super().decode_io(file_io)

        is_server_length = self.decode_bytes_length_io(file_io)
        is_server = int.from_bytes(file_io.read(is_server_length), "big")

        connection_name_length = self.decode_bytes_length_io(file_io)
        connection_name = file_io.read(connection_name_length).decode()
        self.is_server = is_server == 1
        self.connection_name = connection_name

    def decode_bytes(self, message_bytes: bytearray):
        message_length = super().decode_bytes(message_bytes)

        is_server_length = self.decode_bytes_length(message_bytes)
        is_server = int.from_bytes(message_bytes[:is_server_length], "big")
        del message_bytes[:is_server_length]

        connection_name_length = self.decode_bytes_length(message_bytes)
        connection_name = message_bytes[:connection_name_length].decode()
        del message_bytes[:connection_name_length]

        self.is_server = is_server == 1
        self.connection_name = connection_name

    def encode_message(self):
        return_bytes = b""

        if self.is_server:
            is_server = 1
        else:
            is_server = 2

        is_server_bytes = bytearray(is_server.to_bytes(sys.getsizeof(is_server), "big"))
        is_server_bytes = is_server_bytes.lstrip(bytes([0]))
        return_bytes += self.encode_bytes_length(len(is_server_bytes)) + is_server_bytes

        connection_name_bytes = self.connection_name.encode("utf-8")

        return return_bytes + self.encode_bytes_length(len(connection_name_bytes)) + connection_name_bytes

    def encode(self, message_bytes=b""):
        return super().encode(self.encode_message())
