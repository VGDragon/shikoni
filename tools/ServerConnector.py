import asyncio

import multiprocessing

import websockets
from websockets.exceptions import ConnectionClosedOK

from message_types.ShikoniMessageConnectClient import ShikoniMessageConnectClient


class ServerConnector:
    def __init__(self, connect_url: str, connect_port: int, connection_name: str, external_on_message, shikoni):
        self.shikoni = shikoni
        self.connect_url = connect_url
        if self.connect_url.startswith("ws://"):
            self.connect_url = self.connect_url[5:]
        self.connect_port = connect_port
        self._connection_name = connection_name
        self._external_on_message = external_on_message
        self._connection_server: multiprocessing.Process = None

    ############# private ######################


    async def _server_loop(self, future):
        await future


    async def _start_server_connection(self, connector_server):
        async with websockets.serve(lambda websocket, path: self._wait_for_message(connector_server, websocket, path), self.connect_url, self.connect_port):
            #async with websockets.serve(self._wait_for_message, self.connect_url, self.connect_port):
            await asyncio.Future()


    async def _wait_for_message(self, connector_server, websocket, path):
        while True:
            try:
                message = await websocket.recv()
                message_class = self.shikoni.encode_message(bytearray(message))
                if isinstance(message_class, ShikoniMessageConnectClient):
                    self.shikoni.message_connection_start(message_class)
                    continue

                self._external_on_message(connector_server, self._connection_name, message_class)
            except websockets.exceptions.ConnectionClosed:
                print("Connection Closed")
                break



    ########### open ##################

    def start_server_connection_as_subprocess(self, connector_server):
        if self._connection_server is None:
            server_process = multiprocessing.Process(target=self.start_server_connection, args=[connector_server])
            self._connection_server = server_process
            server_process.start()
            return server_process
        return None


    def start_server_connection(self, connector_server):
        asyncio.run(self._start_server_connection(connector_server))

    def close_server_connection(self):
        if self._connection_server is not None:
            self._connection_server.terminate()
