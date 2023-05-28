from typing import BinaryIO

from shikoni.interfaces.ShikoniMessage import ShikoniMessage
from shikoni.base_messages.MessageType import MessageType


class ShikoniMessageRemoveConnectorFromGroup(ShikoniMessage):

    def __init__(self, message=None, message_type: MessageType = None, shikoni=None):
        super().__init__(message, message_type, shikoni)
        self.message_type.type_id = 8  # Remove Connectors Group
        self.group_name: str = ""
        self.connector_name_list: list = []

    def set_variables(self, group_name: str, connector_name_list: list):
        self.group_name = group_name
        self.connector_name_list: list = connector_name_list
        return self


    ############### MESSAGE ENCODE FUNCTION ################
    def encode_message(self):
        return_bytes = self.encode_bytes_length(len(self.group_name))
        return_bytes += self.group_name.encode("utf-8")

        connector_name_list_length = len(self.connector_name_list)

        return_bytes += self.encode_bytes_length(connector_name_list_length)
        for message_item in self.connector_name_list:
            return_bytes += message_item.encode()

        return return_bytes

    ############### ShikoniMessage FUNCTION ################
    def decode_io(self, file_io: BinaryIO):
        message_length = super().decode_io(file_io)

        group_name_length = self.decode_bytes_length_io(file_io)
        group_name = file_io.read(group_name_length).decode()

        message_list_length = self.decode_bytes_length_io(file_io)

        connector_name_list = []
        for _ in range(message_list_length):
            connector_name_list.append(self.shikoni.decode_message_from_file(file_io))

        self.group_name = group_name
        self.connector_name_list = connector_name_list

    def decode_bytes(self, message_bytes: bytearray):
        message_length = super().decode_bytes(message_bytes)

        group_name_length = self.decode_bytes_length(message_bytes)
        group_name = message_bytes[:group_name_length].decode()
        del message_bytes[:group_name_length]

        message_list_length = self.decode_bytes_length(message_bytes)
        connector_name_list = []
        for _ in range(message_list_length):
            connector_name_list.append(self.shikoni.decode_message(message_bytes))

        self.group_name = group_name
        self.connector_name_list = connector_name_list

    def encode(self, message_bytes=b""):
        return super().encode(self.encode_message())


