import json
import time
from typing import BinaryIO

from multiprocessing.managers import BaseManager
import multiprocessing

from tools.PackageController import PackageController
from message_types.MessageType import MessageType
from tools.ClientConnector import ClientConnector
from tools.ServerConnector import ServerConnector
from tools.ServerConnectorData import ConnectorProcess

from message_types.ShikoniMessageConnectClient import ShikoniMessageConnectClient


class ConnectorDataManager(BaseManager):
    # nothing
    pass


class ShikoniClasses:
    connections_clients = []
    connections_server = []  # TODO message from server to 1 client
    do_running = True
    connector_data_manager = ConnectorDataManager()

    def __init__(self, message_type_decode_file: str):
        self.message_type_decode_file = message_type_decode_file
        self.package_controller = PackageController()
        with open(message_type_decode_file) as f:
            self.message_type_dictionary = json.loads(f.read())

        ConnectorDataManager.register('ServerConnector', ServerConnector)
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
            connector_client.close_all_client_connection()

    def message_connection_start(self, connect_client: ShikoniMessageConnectClient):
        self.start_client_connection(connect_client.message[1], connect_client.message[0])

    def start_server_connection(self, url: str, port: int, got_message_call, connection_name: str):
        self.connector_data_manager.start()
        connector_server = self.connector_data_manager.ServerConnector()
        connector_server.set_got_message_call(got_message_call)
        connector_server.set_shikoni(self)
        # connector_server = Connector(got_message_call=got_message_call, shikoni=self)
        connector_server.start_server_connection_as_subprocess(connector_server=connector_server,
                                                               connect_url=url,
                                                               connect_port=port,
                                                               connection_name=connection_name)
        self.connections_server.append(connector_server)
        return connector_server

    def start_server_connections(self, got_message_call, connection_data_list: list):
        self.connector_data_manager.start()
        connector_server = self.connector_data_manager.ServerConnector()
        connector_server.set_got_message_call(got_message_call)
        connector_server.set_shikoni(self)
        return_list = []
        for connection_data in connection_data_list:
            server_process = multiprocessing.Process(target=connector_server.start_server_procress,
                                                     args=[connector_server,
                                                           connection_data.url,
                                                           connection_data.port,
                                                           connection_data.connection_name])
            server_process.start()
            connector_server.prepare_server_dict(connection_data.connection_name)
            self.connections_server.append(connector_server)

            return_list.append(ConnectorProcess(connector_server_class=connector_server,
                                                server_process=server_process,
                                                connection_name=connection_data.connection_name))
        return return_list

    def start_client_connection(self, url: str, port: int):
        client_connector = ClientConnector(connect_url=url, connect_port=port, shikoni=self)
        client_connector.start_connection()
        self.connections_clients.append(client_connector)
        return client_connector

    def close_server(self, connector_process: ConnectorProcess):
        connector_process.server_process.terminate()
        connector_process.connector_server_class.remove_server_connection(connector_process.connection_name)

        if len(self.connections_server) == 0:
            self.connector_data_manager.shutdown()

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
        message_class.decode_bytes(message_bytes)
        return message_class
