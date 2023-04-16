import asyncio

import multiprocessing
from typing import Dict
from interfaces.ShikoniMessage import ShikoniMessage

import websockets
from websockets.exceptions import ConnectionClosedOK


class ServerConnector:
    _message_query: Dict[str, list[ShikoniMessage]] = {}  # TODO check if typing is right
    _lock = multiprocessing.Lock()

    def __init__(self):
        self.shikoni = None
        self._external_on_message = None
        self._external_on_base_message = None
        self._encode_message = None

    def set_got_message_call(self, extern_function):
        self._external_on_message = extern_function

    def set_got_base_message_call(self, extern_function):
        self._external_on_base_message = extern_function

    def set_shikoni(self, shikoni):
        self.shikoni = shikoni

    ############# private ######################

    async def _server_loop(self, future):
        await future

    async def _start_server_connection(self, connect_url, connect_port, connection_name, is_base_server=False):

        if connect_url.startswith("ws://"):
            connect_url = connect_url[5:]
        async with websockets.serve(lambda websocket, path: self._wait_for_message(connection_name, websocket, path, is_base_server), connect_url, connect_port):
            #async with websockets.serve(self._wait_for_message, self.connect_url, self.connect_port):
            await asyncio.Future()

    async def _wait_for_message(self, connection_name, websocket, path, is_base_server=False):
        while True:
            try:
                message = await websocket.recv()
                message_class = self.shikoni.encode_message(bytearray(message))
                if message_class.message_type.type_id < 100 and is_base_server:
                    self._external_on_base_message(message_class)
                    continue
                if is_base_server:
                    continue
                self._lock.acquire()
                self._handle_message_to_send(connection_name, message_class)
                self._lock.release()
            except websockets.exceptions.ConnectionClosed:
                print("Connection Closed")
                break

    def _handle_message_to_send(self, connection_name: str, message_class):
        self._message_query[connection_name].append(message_class)
        messages_got_dict = {}
        for server_connection_name, message_class_list in self._message_query.items():
            if len(message_class_list) > 0:
                messages_got_dict[server_connection_name] = message_class_list[0]
        if len(messages_got_dict) != len(self._message_query):
            return

        for server_connection_name, message_class_list in self._message_query.items():
            message_class_list.pop(0)

        self._external_on_message(messages_got_dict)

    def start_server_connection_handler(self, connect_url, connect_port, connection_name, is_base_server=False):
        asyncio.run(self._start_server_connection(connect_url, connect_port, connection_name, is_base_server))

    def prepare_server_dict(self, connection_name):
        self._message_query[connection_name] = []

    ########### open ##################

    def start_server_connection_as_subprocess(self, connector_server, connect_url, connect_port, connection_name):
        server_process = multiprocessing.Process(target=self.start_server_procress, args=[connector_server, connect_url, connect_port, connection_name])
        connector_server.prepare_server_dict(connection_name)
        server_process.start()

    @staticmethod
    def start_server_procress(connector_server, connect_url, connect_port, connection_name, is_base_server=False):
        connector_server.start_server_connection_handler(connect_url, connect_port, connection_name, is_base_server)

    def remove_server_connection(self, connection_name: str):
        if connection_name in self._message_query:
            self._message_query[connection_name].clear()
            self._message_query.pop(connection_name)

    def remove_all_server_connection(self):
        for key, connector_server in self._message_query.items():
            connector_server.clear()
        self._message_query.clear()
