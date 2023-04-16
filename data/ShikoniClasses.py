import json
import time
from typing import BinaryIO
from multiprocessing import Process
from typing import Dict

from multiprocessing.managers import BaseManager
import multiprocessing

from tools.PackageController import PackageController
from message_types.MessageType import MessageType
from tools.ClientConnector import ClientConnector
from tools.ServerConnector import ServerConnector
from tools.ServerConnectorData import ConnectorProcess

from message_types.ShikoniMessageAddConnector import ShikoniMessageAddConnector


class ConnectorDataManager(BaseManager):
    # nothing
    pass


class ShikoniClasses:
    connections_server: Dict[str, Process] = {}  # TODO check if typing is right
    base_connection_server = None
    connections_clients = []
    do_running = True
    connector_data_manager = ConnectorDataManager()

    def __init__(self, message_type_decode_file: str, default_server_call_function=None, base_server_call_function=None):
        self.message_type_decode_file = message_type_decode_file
        self.package_controller = PackageController()
        with open(message_type_decode_file) as f:
            self.message_type_dictionary = json.loads(f.read())
        self.default_server_call_function = default_server_call_function

        ConnectorDataManager.register('ServerConnector', ServerConnector)
        self.connector_data_manager.start()
        self.connector_server = self.connector_data_manager.ServerConnector()
        self.connector_server.set_got_message_call(self.default_server_call_function)
        self.connector_server.set_got_base_message_call(self.base_server_call_function)
        self.connector_server.set_shikoni(self)

    def base_server_call_function(self, connection_name, message_class):
        if isinstance(message_class, ShikoniMessageAddConnector):
            self.message_connection_start(message_class)

    def shutdown_manager(self):
        self.connector_data_manager.shutdown()

    def wait_until_closed(self):
        while self.do_running:
            time.sleep(1.0)
        self.close_all_client_connections()
        self.close_all_server_connections()

    def message_connection_start(self, shikoni_message_add_connector: ShikoniMessageAddConnector):
        client_connections = []
        server_connections = []
        for connection_item in shikoni_message_add_connector.message:
            if connection_item.is_server:
                server_connections.append(connection_item)
            else:
                client_connections.append(connection_item)

        self.start_server_connections(server_connections)
        self.start_client_connections(client_connections)
        print()  # TODO
        # self.start_client_connection(connect_client.message[1], connect_client.message[0])

    def start_server_connection(self, connection_data):

        if connection_data.connection_name in self.connections_server:
            return
        server_process = multiprocessing.Process(target=self.connector_server.start_server_procress,
                                                 args=[self.connector_server,
                                                       connection_data.url,
                                                       connection_data.port,
                                                       connection_data.connection_name])
        self.connector_server.prepare_server_dict(connection_data.connection_name)
        self.connections_server[connection_data] = server_process
        server_process.start()

    def start_base_server_connection(self, connection_data):

        if connection_data.connection_name in self.connections_server:
            return
        server_process = multiprocessing.Process(target=self.connector_server.start_server_procress,
                                                 args=[self.connector_server,
                                                       connection_data.url,
                                                       connection_data.port,
                                                       connection_data.connection_name,
                                                       True])
        self.base_connection_server = server_process
        server_process.start()

    def close_base_server(self):
        self.base_connection_server.terminate()
        self.base_connection_server = None

    def start_server_connections(self, connection_data_list: list):
        return_list = []
        for connection_data in connection_data_list:
            if connection_data.connection_name in self.connections_server:
                continue
            server_process = multiprocessing.Process(target=self.connector_server.start_server_procress,
                                                     args=[self.connector_server,
                                                           connection_data.url,
                                                           connection_data.port,
                                                           connection_data.connection_name])
            self.connector_server.prepare_server_dict(connection_data.connection_name)
            self.connections_server[connection_data] = server_process
            server_process.start()
            return_list.append(connection_data.connection_name)
        return return_list

    def start_client_connection(self, shikoni_message_connector_socket):
        client_connector = ClientConnector(
            connect_url=shikoni_message_connector_socket.url,
            connect_port=shikoni_message_connector_socket.port,
            shikoni=self)
        client_connector.start_connection()
        self.connections_clients.append(client_connector)
        return client_connector

    def start_client_connections(self, shikoni_message_connector_socket_list: list):
        added_clients = []
        for shikoni_message_connector_socket in shikoni_message_connector_socket_list:
            client_connector = ClientConnector(
                connect_url=shikoni_message_connector_socket.url,
                connect_port=shikoni_message_connector_socket.port,
                shikoni=self)
            client_connector.start_connection()
            self.connections_clients.append(client_connector)
            added_clients.append(client_connector)
        return added_clients

    def close_server(self, connection_names: str):
        if connection_names in self.connections_server:
            self.connections_server.pop(connection_names).terminate()
            self.connector_server.remove_server_connection(connection_names)


    def close_all_server_connections(self):
        for connection_names, connector_server in self.connections_server.items():
            self.connections_server.pop(connection_names).terminate()
            self.connector_server.remove_server_connection(connection_names)
        self.connections_server.clear()

    def close_all_client_connections(self):
        for connector_client in self.connections_clients:
            connector_client.close_all_client_connection()

    def close_all_clients(self):
        while len(self.connections_clients) > 0:
            self.connections_clients.pop(0).close_connection()

    def send_to_all_clients(self, message):
        for client_connector in self.connections_clients:
            client_connector.send_message(message)

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
        message_class.shikoni = self
        message_class.decode_bytes(message_bytes)
        return message_class
