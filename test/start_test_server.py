import sys

from shikoni.tools.ShikoniInfo import start_shikoni_api

from shikoni.ShikoniClasses import ShikoniClasses
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket

def on_message(msg, shikoni):
    for key, item in msg.items():
        print(key, item)

def start_base_shikoni_server(server_port: int, api_port: int):
    api_server = start_shikoni_api(api_port)
    shikoni = ShikoniClasses(default_server_call_function=on_message)

    shikoni.start_base_server_connection(
        ShikoniMessageConnectorSocket().set_variables(url="0.0.0.0",
                                                      port=server_port,
                                                      is_server=True,
                                                      connection_name="001"))
    api_server.terminate()

if __name__ == '__main__':
    shikoni = ShikoniClasses(default_server_call_function=on_message)
    # 1 PORT (server)
    # 2 client or None

    args = sys.argv
    server_port = 0
    api_server_port = 0
    if len(args) > 2:
        server_port = int(args[1])
        api_server_port = int(args[2])

    if server_port > 0:

        start_base_shikoni_server(server_port, api_server_port)
