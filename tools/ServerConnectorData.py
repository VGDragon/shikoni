class ConnectorSocket:

    def __init__(self, url: str, port: int, connection_name: str, is_server: bool = True):
        self.url: str = url
        self.port: int = port
        self.connection_name: str = connection_name
        self.is_server = is_server


class ConnectorProcess:

    def __init__(self, connector_server_class, server_process, connection_name):
        self.connector_server_class = connector_server_class
        self.server_process = server_process
        self.connection_name = connection_name

