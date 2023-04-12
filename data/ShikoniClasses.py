import json
import time
from typing import BinaryIO


from tools.PackageController import PackageController
from message_types.MessageType import MessageType
from interfaces.Connector import Connector

from message_types.ShikoniMessageConnectClient import ShikoniMessageConnectClient


class ShikoniClasses:
    connections_clients = []
    connections_server = []  # TODO message from server to 1 client
    do_running = True

    def __init__(self, message_type_decode_file: str):
        self.message_type_decode_file = message_type_decode_file
        self.package_controller = PackageController()
        with open(message_type_decode_file) as f:
            self.message_type_dictionary = json.loads(f.read())
        # TODO add Connector

    def wait_until_closed(self):
        while self.do_running:
            time.sleep(1.0)
        self.close_all_client_connections()
        self.close_all_server_connections()

    def close_all_server_connections(self):
        for connector_server in self.connections_server:
            connector_server.close_server_connection()

    def close_all_client_connections(self):
        for connector_client in self.connections_clients:
            connector_client.close_client_connection()

    def message_client_start(self, connect_client: ShikoniMessageConnectClient):
        self.start_client_connection(connect_client.message[1], connect_client.message[0])

    def start_server_connection(self, url: str, port: int, got_message_call):
        connector_server = Connector(url, port, self)
        connector_server.start_server_connection_as_subprocess(got_message_call)
        self.connections_server.append(connector_server)
        return connector_server

    def start_client_connection(self, url: str, port: int):
        connector_client = Connector(url, port, self)
        connector_client.start_client_connection()

        self.connections_clients.append(connector_client)
        return connector_client

    def close_server(self, connector_server: Connector):
        connector_server.close_server_connection()
        if connector_server in self.connections_server:
            self.connections_server.remove(connector_server)

    def close_client(self, connector_client: Connector):
        connector_client.close_client_connection()
        if connector_client in self.connections_clients:
            self.connections_clients.remove(connector_client)


    def get_message_class(self, type_id: int):
        self.package_controller.import_module([self.message_type_dictionary[str(type_id)]])

    def encode_message_from_file(self, file_io: BinaryIO):
        message_type = MessageType()
        message_type.decode_io(file_io)
        message_class_info = self.message_type_dictionary[str(message_type.type_id)]

        message_class = self.package_controller.get_module_class(
            package_import_path=message_class_info["module"],
            class_name=message_class_info["class"])
        message_class.decode_io(file_io)
        return message_class

    def encode_message(self, message_bytes: bytearray):
        message_type = MessageType()
        message_type.decode_bytes(message_bytes)
        message_class_info = self.message_type_dictionary[str(message_type.type_id)]

        message_class = self.package_controller.get_module_class(
            package_import_path=message_class_info["module"],
            class_name=message_class_info["class"])
        message_class.decode_bytes(message_bytes)
        return message_class



