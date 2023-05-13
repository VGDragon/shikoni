from typing import BinaryIO

from shikoni.interfaces.ShikoniMessage import ShikoniMessage
from shikoni.base_messages.MessageType import MessageType


class ShikoniMessageAddConnectorGroup(ShikoniMessage):

    def __init__(self, message=None, message_type: MessageType = None, shikoni=None):
        super().__init__(message, message_type, shikoni)
        self.message_type.type_id = 5  #
        self.group_name = ""
        self.connector_socket_list = []  # ShikoniMessageConnectorSocket

    def set_variables(self, group_name: str, connector_socket_list: list):
        self.group_name = group_name
        self.connector_socket_list: list = connector_socket_list
        return self

    ############### MESSAGE ENCODE FUNCTION ################
    def encode_message(self):
        return_bytes = self.encode_bytes_length(len(self.group_name))
        return_bytes += self.group_name.encode("utf-8")

        connector_socket_list_length = len(self.connector_socket_list)

        return_bytes += self.encode_bytes_length(connector_socket_list_length)
        for message_item in self.connector_socket_list:
            return_bytes += message_item.encode()

        return return_bytes

    ############### ShikoniMessage FUNCTION ################
    def decode_io(self, file_io: BinaryIO):
        message_length = super().decode_io(file_io)

        group_name_length = self.decode_bytes_length_io(file_io)
        group_name = file_io.read(group_name_length).decode()

        message_list_length = self.decode_bytes_length_io(file_io)

        connector_socket_list = []
        for _ in range(message_list_length):
            connector_socket_list.append(self.shikoni.decode_message_from_file(file_io))

        self.group_name = group_name
        self.connector_socket_list = connector_socket_list

    def decode_bytes(self, message_bytes: bytearray):
        message_length = super().decode_bytes(message_bytes)

        group_name_length = self.decode_bytes_length(message_bytes)
        group_name = message_bytes[:group_name_length].decode()
        del message_bytes[:group_name_length]

        message_list_length = self.decode_bytes_length(message_bytes)
        connector_socket_list = []
        for _ in range(message_list_length):
            connector_socket_list.append(self.shikoni.decode_message(message_bytes))

        self.group_name = group_name
        self.connector_socket_list = connector_socket_list

    def encode(self, message_bytes=b""):
        return super().encode(self.encode_message())
