from websockets.sync.client import connect as client_connect
from websockets.sync.client import ClientConnection

class ClientConnector:

    def __init__(self, connect_url: str, connect_port: int, shikoni, connection_name):
        self.shikoni = shikoni
        self.connect_url = connect_url
        if not self.connect_url.startswith("ws://"):
            self.connect_url = "ws://" + self.connect_url
        self.connect_port = connect_port
        self._connection_client: ClientConnection = None
        self.connection_name = connection_name

    ########### open ##################


    def start_connection(self):
        if self._connection_client is None:
            self._connection_client = client_connect(
                "{0}:{1}".format(self.connect_url, self.connect_port))


    def close_connection(self):
        if self._connection_client is not None:
            self._connection_client.close()
            self.shikoni.connections_clients.pop(self.connection_name)
            self._connection_client = None

    def send_message(self, message):
        if isinstance(message, bytes):
            self._connection_client.send(message)
        else:
            self._connection_client.send(message.encode())
