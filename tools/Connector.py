import asyncio

import multiprocessing
from typing import Dict
from multiprocessing.managers import BaseManager

import websockets
from websockets.exceptions import ConnectionClosedOK

from websockets.sync.client import connect as client_connect

from message_types.ShikoniMessageConnectClient import ShikoniMessageConnectClient
from interfaces.ShikoniMessage import ShikoniMessage

from tools.ClientConnector import ClientConnector
from tools.ServerConnector import ServerConnector


class Connector:
    _connection_server_dic: Dict[str, ServerConnector] = {}  # TODO check if typing is right
    _message_query: Dict[str, list[ShikoniMessage]] = {}  # TODO check if typing is right

    _lock = multiprocessing.Lock()

    def __init__(self):
        self.shikoni = None
        self._external_on_message = None

    def set_got_message_call(self, extern_function):
        self._external_on_message = extern_function

    def set_shikoni(self, shikoni):
        self.shikoni = shikoni

    def setup_message_query_for_connection(self, connection_name):
        self._message_query[connection_name] = []

    def add_to_message_query(self, connection_name, message_class):
        self._message_query[connection_name].append(message_class)

    def handle_message_to_send(self, connection_name: str, message_class_list):
        self._message_query[connection_name].append(message_class_list)
        messages_got_dict = {}
        for server_connection_name, message_class_list in self._message_query.items():
            if len(message_class_list) > 0:
                messages_got_dict[server_connection_name] = message_class_list[0]
        if len(messages_got_dict) != len(self._message_query):
            return

        for server_connection_name, message_class_list in self._message_query.items():
            message_class_list.pop(0)

        self._external_on_message(messages_got_dict)

    def add_lock(self):
        self._lock.acquire()

    def release_lock(self):
        self._lock.release()


    ############# private ######################

    @staticmethod
    def _on_message(self, connection_name: str, message_class):
        # TODO make it multiprocessing save
        self.add_lock()
        self.handle_message_to_send(connection_name, message_class)
        self.release_lock()

    ########### open ##################

    def start_server_connection(self,
                                connect_url: str,
                                connect_port: int,
                                connection_name: str,
                                connector_server):
        if connection_name not in self._connection_server_dic and connection_name not in self._message_query:
            print()
            server_connector = ServerConnector(connect_url=connect_url,
                                               connect_port=connect_port,
                                               connection_name=connection_name,
                                               external_on_message=self._on_message,
                                               shikoni=self.shikoni)
            server_connector.start_server_connection_as_subprocess(connector_server)
            self._connection_server_dic[connection_name] = server_connector
            connector_server.setup_message_query_for_connection(connection_name)
            self._message_query[connection_name] = []
            #return server_connector
        return None

    def close_server_connection(self, connection_name: str):
        if connection_name in self._connection_server_dic:
            self._connection_server_dic.pop(connection_name).close_server_connection()
            if connection_name in self._message_query:
                self._message_query[connection_name].clear()

    def close_all_server_connection(self):
        temp_connections = self._connection_server_dic.copy()
        self._connection_server_dic.clear()
        for connection_name, server_connection in temp_connections:
            server_connection.close_server_connection()
            if connection_name in self._message_query:
                self._message_query[connection_name].clear()
