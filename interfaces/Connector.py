import asyncio

import multiprocessing
import websockets
from websockets.exceptions import ConnectionClosedOK

from websockets.sync.client import connect as client_connect
from websockets.sync.client import ClientConnection

from message_types.ShikoniMessageConnectClient import ShikoniMessageConnectClient


class Connector:

    def __init__(self, connect_url: str, connect_port: int, shikoni):
        self.shikoni = shikoni
        self.connect_url = connect_url
        if self.connect_url.startswith("ws://"):
            self.connect_url = self.connect_url[5:]
        self.connect_port = connect_port
        self._external_on_message = None
        self._connection_client: ClientConnection = None
        self._connection_server: multiprocessing.Process = None

    ############# private ######################

    async def _server_loop(self, future):
        await future

    async def _start_server_connection(self, got_message_call):
        self._external_on_message = got_message_call
        async with websockets.serve(self._wait_for_message, self.connect_url, self.connect_port):
            await asyncio.Future()

    async def _wait_for_message(self, websocket, path):
        while True:
            try:
                message = await websocket.recv()
                message_class = self.shikoni.encode_message(bytearray(message))
                if isinstance(message_class, ShikoniMessageConnectClient):
                    self.shikoni.message_client_start(message_class)
                else:
                    self._external_on_message(message_class)
            except websockets.exceptions.ConnectionClosed:
                print("Connection Closed")
                break


    ########### open ##################

    def start_server_connection_as_subprocess(self, got_message_call):

        server_process = multiprocessing.Process(target=self.start_server_connection, args=[got_message_call])

        #server_process = multiprocessing.Pool(1)
        #server_process.map(self.start_server_connection, [got_message_call])
        #multiprocessing.ProcessingPool().
        server_process.start()
        #server_process.terminate()
        self._connection_server = server_process
        return server_process


    def start_server_connection(self, got_message_call):
        asyncio.run(self._start_server_connection(got_message_call))

    def start_client_connection(self):
        self._connection_client = client_connect("ws://{0}:{1}".format(self.connect_url, self.connect_port))

    def close_client_connection(self):
        if self._connection_client is not None:
            self._connection_client.close()

    def close_server_connection(self):
        if self._connection_server is not None:
            self._connection_server.terminate()

    def send_message(self, message):
        if isinstance(message, bytes):
            self._connection_client.send(message)
        else:
            self._connection_client.send(message.encode())
