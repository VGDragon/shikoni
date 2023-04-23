import asyncio
import multiprocessing

from multiprocessing import Process
from multiprocessing import Queue

from typing import Dict
from interfaces.ShikoniMessage import ShikoniMessage

import websockets
from websockets.exceptions import ConnectionClosedOK


class ServerConnector:

    def __init__(self, shikoni, external_on_base_messag, external_on_message):
        self.shikoni = shikoni
        self._external_on_message = external_on_message
        self._external_on_base_message = external_on_base_messag
        self.is_running = True

        self.connections_server: Dict[str, Process] = {}  # TODO check if typing is right
        self._message_query: Dict[str, list[ShikoniMessage]] = {}  # TODO check if typing is right

        # self.message_query_class = Queue()
        self.message_query_class = Queue()
        self.sub_pc = []


    ############# private ######################

    async def _server_loop(self, future):
        await future

    def server_loop(self):
        while self.is_running:
            message_dict = None
            try:
                message_dict = self.message_query_class.get(timeout=10.0)
            except:
                pass
            if message_dict is None:
                continue
            message_class = self.shikoni.encode_message(bytearray(message_dict["message"]))
            if message_class.message_type.type_id < 100:
                self._external_on_base_message(message_class)
                continue
            if message_dict["is_base_server"]:
                continue
            #self._lock.acquire()
            self._handle_message_to_send(message_dict["connection_name"], message_class)
            #self._lock.release()

    async def _start_server_connection(self, message_queue, connect_url, connect_port, connection_name, is_base_server=False):

        if connect_url.startswith("ws://"):
            connect_url = connect_url[5:]
        async with websockets.serve(lambda websocket, path: self._wait_for_message(message_queue, connection_name, websocket, path, is_base_server), connect_url, connect_port):
            #async with websockets.serve(self._wait_for_message, self.connect_url, self.connect_port):
            await asyncio.Future()


    async def _wait_for_message(self, message_queue, connection_name, websocket, path, is_base_server=False):
        while True:
            try:
                message = await websocket.recv()
                message_queue.put({"connection_name": connection_name, "is_base_server": is_base_server, "message": message})
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

    def start_server_connection_handler(self, message_queue, connect_url, connect_port, connection_name, is_base_server=False):
        asyncio.run(self._start_server_connection(message_queue, connect_url, connect_port, connection_name, is_base_server))

    def prepare_server_dict(self, connection_name):
        self._message_query[connection_name] = []

    ########### open ##################

    def start_server_connection_as_subprocess(self, connect_url, connect_port, connection_name, is_base_server=False):
        server_process = Process(target=self.start_server_procress, args=[self.message_query_class, connect_url, connect_port, connection_name, is_base_server])
        self.prepare_server_dict(connection_name)
        server_process.start()
        self.connections_server[connection_name] = server_process
        return server_process

    def start_server_procress(self, message_queue, connect_url, connect_port, connection_name, is_base_server=False):
        self.start_server_connection_handler(message_queue, connect_url, connect_port, connection_name, is_base_server)

    def remove_server_connection(self, connection_name: str):
        if connection_name in self._message_query:
            self._message_query[connection_name].clear()
            self._message_query.pop(connection_name)

    def remove_all_server_connection(self):
        for key, connector_server in self._message_query.items():
            connector_server.clear()
        self._message_query.clear()
