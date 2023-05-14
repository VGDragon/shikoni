import json
import time
from typing import BinaryIO
from multiprocessing import Process
from typing import Dict

from shikoni.data.MessageTypeClasses import get_message_type_classes

from shikoni.tools.PackageController import PackageController
from shikoni.base_messages.MessageType import MessageType
from shikoni.tools.ClientConnector import ClientConnector
from shikoni.tools.ServerConnector import ServerConnector

from shikoni.base_messages.ShikoniMessageAddConnector import ShikoniMessageAddConnector
from shikoni.base_messages.ShikoniMessageRemoveConnector import ShikoniMessageRemoveConnector

from shikoni.base_messages.ShikoniMessageAddConnectorGroup import ShikoniMessageAddConnectorGroup
from shikoni.base_messages.ShikoniMessageRemoveConnectorGroup import ShikoniMessageRemoveConnectorGroup


from shikoni.base_messages.ShikoniMessageAddConnectorToGroup import ShikoniMessageAddConnectorToGroup
from shikoni.base_messages.ShikoniMessageRemoveConnectorFromGroup import ShikoniMessageRemoveConnectorFromGroup

from shikoni.base_messages.ShikoniMessageConnectorName import ShikoniMessageConnectorName
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket


class ShikoniClasses:
    connections_server: Dict[str, Process] = {}
    base_connection_server = None
    connections_clients: Dict[str, ClientConnector] = {}
    do_running = True

    connection_group: Dict[str, Dict[str, Dict[str, ClientConnector]]] = {}

    def __init__(self, default_server_call_function=None,
                 message_type_decode_file: str = None):
        self.message_type_decode_file = message_type_decode_file
        self.message_type_dictionary = get_message_type_classes(message_type_decode_file)

        self.package_controller = PackageController()
        self.default_server_call_function = default_server_call_function
        self.connector_server = ServerConnector(
            shikoni=self,
            external_on_base_messag=self.base_server_call_function,
            external_on_message=self.default_server_call_function)
        #self.message_query_class = Queue()

    ########### CAll FUNCTIONS #################

    def base_server_call_function(self, message_class):
        if isinstance(message_class, ShikoniMessageAddConnector):
            self.message_connection_start(message_class)
        elif isinstance(message_class, ShikoniMessageRemoveConnector):
            self.message_connection_close(message_class)
        elif isinstance(message_class, ShikoniMessageAddConnectorGroup):
            self.start_connection_group(message_class)
        elif isinstance(message_class, ShikoniMessageRemoveConnectorGroup):
            self.close_connection_group(message_class)
        elif isinstance(message_class, ShikoniMessageAddConnectorToGroup):
            self.add_connection_to_group(message_class)
        elif isinstance(message_class, ShikoniMessageRemoveConnectorFromGroup):
            self.remove_connection_from_group(message_class)

    ########### MESSAGE CALL FUNCTIONS #################

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

    def message_connection_close(self, shikoni_message_add_connector: ShikoniMessageRemoveConnector):
        client_connections = []
        server_connections = []
        for connection_item in shikoni_message_add_connector.message:
            if connection_item.is_server:
                server_connections.append(connection_item.connection_name)
            else:
                client_connections.append(connection_item.connection_name)

        self.close_server_connections(server_connections)
        self.close_client_connections(client_connections)

    ########### MESSAGE DECODE FUNCTIONS #################

    def decode_message_from_file(self, file_io: BinaryIO):
        message_type = MessageType()
        message_type.decode_io(file_io)
        message_class_info = self.message_type_dictionary[str(message_type.type_id)]

        message_class = self.package_controller.get_module_class(
            package_import_path=message_class_info["module"],
            class_name=message_class_info["class"])
        message_class.decode_io(file_io)
        return message_class

    def decode_message(self, message_bytes: bytearray):
        message_type = MessageType()
        message_type.decode_bytes(message_bytes)
        message_class_info = self.message_type_dictionary[str(message_type.type_id)]

        message_class = self.package_controller.get_module_class(
            package_import_path=message_class_info["module"],
            class_name=message_class_info["class"])
        message_class.shikoni = self
        message_class.decode_bytes(message_bytes)
        return message_class

    ########### BASE SERVER FUNCTIONS #################

    def start_base_server_connection(self, connection_data, start_loop: bool = True):
        if connection_data.connection_name in self.connections_server:
            return

        server_process = self.connector_server.start_server_connection_as_subprocess(connection_data.url,
                                                                                     connection_data.port,
                                                                                     connection_data.connection_name,
                                                                                     is_base_server=True)
        # self.connector_server.prepare_server_dict(connection_data.connection_name)
        self.base_connection_server = server_process
        if start_loop:
            self.connector_server.server_loop()
        return self.connector_server

    def close_base_server(self):
        self.base_connection_server.terminate()
        self.base_connection_server = None

    ########### SERVER FUNCTIONS #################

    def start_server_connections(self, connection_data_list: list):
        return_list = []
        for connection_data in connection_data_list:
            if connection_data.connection_name in self.connections_server:
                continue
            server_process = self.connector_server.start_server_connection_as_subprocess(connection_data.url,
                                                                                         connection_data.port,
                                                                                         connection_data.connection_name)
            # self.connector_server.prepare_server_dict(connection_data.connection_name)
            self.connections_server[connection_data.connection_name] = server_process
            return_list.append(connection_data.connection_name)
        return return_list

    def close_server_connections(self, server_connections):
        for connection_names in server_connections:
            if connection_names in self.connections_server:
                self.connections_server.pop(connection_names).terminate()
                self.connector_server.remove_server_connection(connection_names)

    def close_all_server_connections(self):
        for connection_names, connector_server in self.connections_server.items():
            self.connections_server.pop(connection_names).terminate()
            self.connector_server.remove_server_connection(connection_names)
        self.connections_server.clear()

    ########### CLIENT FUNCTIONS #################

    def start_client_connection(self, shikoni_message_connector_socket):
        if shikoni_message_connector_socket.connection_name not in self.connections_clients:
            client_connector = ClientConnector(
                connect_url=shikoni_message_connector_socket.url,
                connect_port=shikoni_message_connector_socket.port,
                shikoni=self,
                connection_name=shikoni_message_connector_socket.connection_name)
            client_connector.start_connection()
            self.connections_clients[shikoni_message_connector_socket.connection_name] = client_connector
            return client_connector

    def start_client_connections(self, shikoni_message_connector_socket_list: list):
        added_clients = {}
        for shikoni_message_connector_socket in shikoni_message_connector_socket_list:
            if shikoni_message_connector_socket.connection_name in self.connections_clients:
                continue
            client_connector = ClientConnector(
                connect_url=shikoni_message_connector_socket.url,
                connect_port=shikoni_message_connector_socket.port,
                shikoni=self,
                connection_name=shikoni_message_connector_socket.connection_name)
            client_connector.start_connection()
            self.connections_clients[shikoni_message_connector_socket.connection_name] = client_connector
            added_clients[shikoni_message_connector_socket.connection_name] = client_connector
        return added_clients

    def close_all_client_connections(self):
        for connection_names, connector_client in self.connections_clients.items():
            connector_client.close_connection()

    def close_client_connections(self, client_connections):
        for connection_name in client_connections:
            if connection_name in self.connections_clients:
                self.connections_clients.pop(connection_name).close_connection()

    ########### CONNECTION GROUP FUNCTIONS #################

    def start_connection_group(self, connector_group_add: ShikoniMessageAddConnectorGroup):  # TODO testing
        if connector_group_add.group_name in self.connection_group:
            return
        connection_group_dict = {
            "server": {},
            "client": {}
        }

        for connection_data in connector_group_add.connector_socket_list:
            if connection_data.is_server:
                if connection_data.connection_name in connection_group_dict["server"]:
                    continue
                server_process = self.connector_server.start_server_connection_as_subprocess(connection_data.url,
                                                                                             connection_data.port,
                                                                                             connection_data.connection_name,
                                                                                             connector_group_add.group_name)
                connection_group_dict["server"][connection_data.connection_name] = server_process
            else:
                if connection_data.connection_name in connection_group_dict["client"]:
                    continue

                client_connector = ClientConnector(
                    connect_url=connection_data.url,
                    connect_port=connection_data.port,
                    shikoni=self,
                    connection_name=connection_data.connection_name)
                client_connector.start_connection()
                connection_group_dict["client"][connection_data.connection_name] = client_connector
        self.connection_group[connector_group_add.group_name] = connection_group_dict
        return connection_group_dict

    def add_connection_to_group(self, connector_group_add: ShikoniMessageAddConnectorToGroup):  # TODO testing
        if connector_group_add.group_name not in self.connection_group:
            return

        for connection_data in connector_group_add.connector_socket_list:
            if connection_data.is_server:
                if connection_data.connection_name in self.connection_group[connector_group_add.group_name]["server"]:
                    continue
                server_process = self.connector_server.start_server_connection_as_subprocess(connection_data.url,
                                                                                             connection_data.port,
                                                                                             connection_data.connection_name,
                                                                                             connector_group_add.group_name)
                self.connection_group[
                    connector_group_add.group_name]["server"][
                    connection_data.connection_name] = server_process
            else:
                if connection_data.connection_name in self.connection_group[connector_group_add.group_name]["client"]:
                    continue

                client_connector = ClientConnector(
                    connect_url=connection_data.url,
                    connect_port=connection_data.port,
                    shikoni=self,
                    connection_name=connection_data.connection_name)
                client_connector.start_connection()
                self.connection_group[connector_group_add.group_name]["client"][connection_data.connection_name] = client_connector
        return self.connection_group[connector_group_add.group_name]


    def close_connection_group(self, connection_group_remove: ShikoniMessageRemoveConnectorGroup):  # TODO testing
        group_name: str = connection_group_remove.message

        if group_name not in self.connection_group:
            return

        connection_group: dict = self.connection_group[group_name]

        for connection_name, server_connector in connection_group["server"].items():
            server_connector.terminate()
            self.connector_server.remove_server_connection(connection_name, group_name)
        connection_group.pop("server")

        for connection_name, client_connector in connection_group["client"].items():
            client_connector.close_connection()
        connection_group.pop("client")

        self.connection_group.pop(group_name)

    def remove_connection_from_group(self, connection_group_remove: ShikoniMessageRemoveConnectorFromGroup):  # TODO testing
        group_name: str = connection_group_remove.group_name

        if group_name not in self.connection_group:
            return

        for connection_name in connection_group_remove.connector_name_list:
            connection_name: ShikoniMessageConnectorName = connection_name
            if connection_name.is_server:
                if connection_name.connection_name not in self.connection_group[group_name]["server"]:
                    continue
                self.connection_group[group_name]["server"][connection_name.connection_name].terminate()
                self.connector_server.remove_server_connection(connection_name.connection_name, group_name)
            else:
                if connection_name.connection_name not in self.connection_group[group_name]["client"]:
                    continue
                self.connection_group[group_name]["server"][connection_name.connection_name].close_connection()



    ########### DIV #################

    def wait_until_closed(self):
        while self.do_running:
            time.sleep(1.0)
        self.close_all_client_connections()
        self.close_all_server_connections()

    def send_to_all_clients(self, message):
        for connection_names, connector_client in self.connections_clients.items():
            connector_client.send_message(message)

    def get_message_class(self, type_id: int):
        self.package_controller.import_module([self.message_type_dictionary[str(type_id)]])
