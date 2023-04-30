import sys
from typing import BinaryIO

from shikoni.interfaces.ShikoniMessage import ShikoniMessage
from shikoni.base_messages.MessageType import MessageType


class ShikoniMessageConnectorSocket(ShikoniMessage):

    def __init__(self, message=None, message_type: MessageType = None, shikoni=None):
        super().__init__(message, message_type, shikoni)
        self.message_type.type_id = 2  # Connector Socket
        self.is_server = True
        self.port: int = 0
        self.url: str = ""
        self.connection_name: str = ""

    def set_variables(self, url: str, port: int, is_server: bool, connection_name: str):
        self.is_server = is_server
        self.port: int = port
        self.url: str = url
        self.connection_name: str = connection_name
        return self

    ############### MESSAGE ENCODE FUNCTION ################

    def encode_message(self):
        return_bytes = b""

        if self.is_server:
            is_server = 1
        else:
            is_server = 2

        is_server_bytes = bytearray(is_server.to_bytes(sys.getsizeof(is_server), "big"))
        is_server_bytes = is_server_bytes.lstrip(bytes([0]))
        return_bytes += self.encode_bytes_length(len(is_server_bytes)) + is_server_bytes

        port_bytes = bytearray(self.port.to_bytes(sys.getsizeof(self.port), "big"))
        port_bytes = port_bytes.lstrip(bytes([0]))
        return_bytes += self.encode_bytes_length(len(port_bytes)) + port_bytes

        url_bytes = self.url.encode("utf-8")
        return_bytes += self.encode_bytes_length(len(url_bytes)) + url_bytes

        connection_name_bytes = self.connection_name.encode("utf-8")

        return return_bytes + self.encode_bytes_length(len(connection_name_bytes)) + connection_name_bytes

    ############### ShikoniMessage FUNCTION ################

    def decode_io(self, file_io: BinaryIO):
        message_length = super().decode_io(file_io)

        is_server_length = self.decode_bytes_length_io(file_io)
        is_server = int.from_bytes(file_io.read(is_server_length), "big")

        port_length = self.decode_bytes_length_io(file_io)
        port = int.from_bytes(file_io.read(port_length), "big")

        url_length = self.decode_bytes_length_io(file_io)
        url = file_io.read(url_length).decode()

        connection_name_length = self.decode_bytes_length_io(file_io)
        connection_name = file_io.read(connection_name_length).decode()
        self.is_server = is_server == 1
        self.port = port
        self.url = url
        self.connection_name = connection_name

    def decode_bytes(self, message_bytes: bytearray):
        message_length = super().decode_bytes(message_bytes)

        is_server_length = self.decode_bytes_length(message_bytes)
        is_server = int.from_bytes(message_bytes[:is_server_length], "big")
        del message_bytes[:is_server_length]

        port_length = self.decode_bytes_length(message_bytes)
        port = int.from_bytes(message_bytes[:port_length], "big")
        del message_bytes[:port_length]

        url_length = self.decode_bytes_length(message_bytes)
        url = message_bytes[:url_length].decode()
        del message_bytes[:url_length]

        connection_name_length = self.decode_bytes_length(message_bytes)
        connection_name = message_bytes[:connection_name_length].decode()
        del message_bytes[:connection_name_length]

        self.is_server = is_server == 1
        self.port = port
        self.url = url
        self.connection_name = connection_name

    def encode(self, message_bytes=b""):
        return super().encode(self.encode_message())
