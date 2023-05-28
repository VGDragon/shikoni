import argparse

from shikoni.ShikoniClasses import ShikoniClasses

from shikoni.tools.ShikoniInfo import start_shikoni_api
from shikoni.message_types.ShikoniMessageString import ShikoniMessageString
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket


def on_message(msg, shikoni):
    # add stuff here

    # example
    for key, item in msg.items():
        if isinstance(item, ShikoniMessageString):
            print(key, item.message)
        else:
            print(key, item)


def start_base_shikoni_server(server_port: int, api_server_port: int, on_message_call, start_loop: bool = True):
    shikoni = ShikoniClasses(message_type_decode_file="data/massage_type_classes.json",
                             default_server_call_function=on_message_call)

    # to search for free ports as client
    api_server = start_shikoni_api(api_server_port)

    # start the websocket server
    # if start_loop is false, no messages will be handled
    shikoni.start_base_server_connection(
        connection_data=ShikoniMessageConnectorSocket().set_variables(url="0.0.0.0",
                                                                      port=server_port,
                                                                      is_server=True,
                                                                      connection_name="001"),
        start_loop=start_loop)
    # shikoni.base_connection_server.server_loop() # if you want to start the loop later
    shikoni.close_base_server()
    api_server.terminate()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Skikoni Server")
    parser.add_argument("-p", "--port", dest="port", type=int, help="server port ()")
    parser.add_argument("--api", dest="api_port", type=int, help="api server port (PORT + 1)")

    args = parser.parse_args()
    server_port = 19998
    if args.port:
        server_port = args.port
    api_server_port = server_port + 1
    if args.api_port:
        api_server_port = args.api_port

    start_base_shikoni_server(server_port=server_port, api_server_port=api_server_port, on_message_call=on_message)
