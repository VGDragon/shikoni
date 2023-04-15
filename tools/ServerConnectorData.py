class ConnectorSocket:

    def __init__(self, url: str, port: int, connection_name: str):
        self.url: str = url
        self.port: int = port
        self.connection_name: str = connection_name


class ConnectorProcess:

    def __init__(self, connector_server_class, server_process, connection_name):
        self.connector_server_class = connector_server_class
        self.server_process = server_process
        self.connection_name = connection_name

