import asyncio

from multiprocessing import Process
from multiprocessing import Queue

from typing import Dict
from shikoni.interfaces.ShikoniMessage import ShikoniMessage
from shikoni.base_messages.ShikoniMessageRemoveConnector import ShikoniMessageRemoveConnector
from shikoni.base_messages.ShikoniMessageRemoveConnectorFromGroup import ShikoniMessageRemoveConnectorFromGroup
from shikoni.base_messages.ShikoniMessageConnectorName import ShikoniMessageConnectorName

import websockets
from websockets.exceptions import ConnectionClosedOK


class ServerConnector:

    def __init__(self, shikoni, external_on_base_messag, external_on_message):
        self.shikoni = shikoni
        self._external_on_message = external_on_message
        self._external_on_base_message = external_on_base_messag
        self.is_running = True

        self.connections_server: Dict[str, Process] = {}
        self.base_server: Process = None
        self._message_query: Dict[str, list[ShikoniMessage]] = {}
        self._message_group_query: Dict[str, Dict[str, list[ShikoniMessage]]] = {}

        # self.message_query_class = Queue()
        self.message_query_class = Queue()
        self.sub_pc = []

    ############# MESSAGE RECIVED FUNCTIONS ######################

    def server_loop(self):
        while self.is_running:
            try:
                message_dict = None
                try:
                    message_dict = self.message_query_class.get(timeout=1.0)
                except KeyboardInterrupt:
                    break
                except:
                    pass
                if message_dict is None:
                    continue
                message_class = self.shikoni.decode_message(bytearray(message_dict["message"]))
                if message_class.message_type.type_id < 100:
                    self._external_on_base_message(message_class)
                    continue
                if message_dict["is_base_server"]:
                    continue
                self._handle_message_to_send(message_dict["connection_name"], message_class, message_dict["group_name"])
            except KeyboardInterrupt:
                break

    def _handle_message_to_send(self, connection_name: str, message_class, group_name=None):
        if group_name is not None:
            self._handle_group_message_to_send(connection_name, message_class, group_name)
            return
        self._message_query[connection_name].append(message_class)
        messages_got_dict = {}
        for server_connection_name, message_class_list in self._message_query.items():
            if len(message_class_list) > 0:
                messages_got_dict[server_connection_name] = message_class_list[0]
        if len(messages_got_dict) != len(self._message_query):
            return

        for server_connection_name, message_class_list in self._message_query.items():
            message_class_list.pop(0)

        self._external_on_message({"group_name": group_name, "messages": messages_got_dict}, self.shikoni)

    def _handle_group_message_to_send(self, connection_name: str, message_class, group_name=None):

        self._message_group_query[group_name][connection_name].append(message_class)
        messages_got_dict = {}
        for server_connection_name, message_class_list in self._message_group_query[group_name].items():
            if len(message_class_list) > 0:
                messages_got_dict[server_connection_name] = message_class_list[0]
        if len(messages_got_dict) != len(self._message_group_query[group_name]):
            return

        for server_connection_name, message_class_list in self._message_group_query[group_name].items():
            message_class_list.pop(0)

        self._external_on_message({"group_name": group_name, "messages": messages_got_dict}, self.shikoni)

    ############# PREPARE CONNECTION FUCTIONS ######################

    def prepare_server_dict(self, connection_name, group_name=None):
        if group_name is None:
            self._message_query[connection_name] = []
        else:
            if group_name not in self._message_group_query:
                self._message_group_query[group_name] = {}
            self._message_group_query[group_name][connection_name] = []

    ############# SERVER FUCTIONS ######################

    def start_server_connection_as_subprocess(self,
                                              connect_url,
                                              connect_port,
                                              connection_name,
                                              is_base_server=False,
                                              group_name=None,
                                              path_to_use: str = ""):
        server_process = Process(target=start_asyncio_server_procress,
                                 args=[self.message_query_class,
                                       connect_url,
                                       connect_port,
                                       connection_name,
                                       is_base_server,
                                       group_name,
                                       path_to_use])
        if is_base_server:
            self.base_server = server_process
        else:
            self.prepare_server_dict(connection_name, group_name=group_name)
        server_process.start()
        if not is_base_server:
            self.connections_server[connection_name] = server_process
        return server_process

    def remove_server_connection(self, connection_name: str, group_name=None):
        if group_name is None:
            if connection_name in self._message_query:
                self._message_query[connection_name].clear()
                self._message_query.pop(connection_name)
        else:
            if group_name not in self._message_group_query:
                return
            self._message_group_query[group_name][connection_name].clear()
            self._message_group_query[group_name].pop(connection_name)

    def remove_all_server_connection(self):
        for key, connector_server in self._message_query.items():
            connector_server.clear()
        self._message_query.clear()


############# SERVER PROCESS FUCTIONS ######################

def start_asyncio_server_procress(message_queue,
                                  connect_url,
                                  connect_port,
                                  connection_name,
                                  is_base_server=False,
                                  group_name=None,
                                  path_to_use: str = ""):
    asyncio.run(start_asyncio_server_connection(
        message_queue=message_queue,
        connect_url=connect_url,
        connect_port=connect_port,
        connection_name=connection_name,
        is_base_server=is_base_server,
        group_name=group_name,
        path_to_use=path_to_use))


async def start_asyncio_server_connection(message_queue,
                                          connect_url,
                                          connect_port,
                                          connection_name,
                                          is_base_server=False,
                                          group_name=None,
                                          path_to_use: str = ""):
    if connect_url.startswith("ws://"):
        connect_url = connect_url[5:]
    async with websockets.serve(lambda websocket, path: _wait_for_message(
            message_queue=message_queue,
            connection_name=connection_name,
            websocket=websocket,
            path=path,
            is_base_server=is_base_server,
            group_name=group_name,
            path_to_use=path_to_use), connect_url, connect_port):
        await asyncio.Future()


async def _wait_for_message(message_queue,
                            connection_name,
                            websocket,
                            path,
                            is_base_server=False,
                            group_name=None,
                            path_to_use: str = ""):
    if not path_to_use.startswith("/"):
        path_to_use = "/" + path_to_use
    if path != path_to_use:
        await websocket.close()
        return
    while True:
        try:
            message = await websocket.recv()
            message_queue.put(
                {"connection_name": connection_name,
                 "is_base_server": is_base_server,
                 "group_name": group_name,
                 "message": message})
        except websockets.exceptions.ConnectionClosed:
            print("Connection Closed")
            break
