import sys
import time

from shikoni.data.ShikoniClasses import ShikoniClasses
from shikoni.message_types.ShikoniMessageString import ShikoniMessageString
from shikoni.base_messages.ShikoniMessageAddConnector import ShikoniMessageAddConnector
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket
from shikoni.base_messages.ShikoniMessageRemoveConnector import ShikoniMessageRemoveConnector
from shikoni.base_messages.ShikoniMessageConnectorName import ShikoniMessageConnectorName


def on_message(msg):
    for key, item in msg.items():
        if isinstance(item, ShikoniMessageString):
            print(key, item.message)
        else:
            print(key, item)


def start_base_shikoni_server(shikoni: ShikoniClasses, server_port: int):
    shikoni.start_base_server_connection(
        ShikoniMessageConnectorSocket().set_variables(url="0.0.0.0",
                                                      port=server_port,
                                                      is_server=True,
                                                      connection_name="001"))
    time.sleep(20.0)
    shikoni.close_base_server()


def start_connection_message_test(shikoni: ShikoniClasses, server_address: str, server_port: int):
    # connect to base server
    connector_base_client = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, server_port, False, "001")
    )

    # start new server connections with base server
    connector_message = ShikoniMessageAddConnector(message=[
        ShikoniMessageConnectorSocket().set_variables("0.0.0.0", 19980, True, "010"),
        ShikoniMessageConnectorSocket().set_variables("0.0.0.0", 19981, True, "011"),
        #ShikoniMessageConnectorSocket().set_variables(server_address, 19999, False, ""),
    ])
    connector_base_client.send_message(connector_message)
    time.sleep(2.0)

    # connect to the first new servers
    connector_client_01 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, 19980, False, "002")
    )
    connector_client_01.send_message(ShikoniMessageString("Testing new server: 1"))
    time.sleep(1.0)
    connector_client_01.close_connection()

    # connect to the second new servers
    connector_client_02 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, 19981, False, "003")
    )
    connector_client_02.send_message(ShikoniMessageString("Testing new server: 2"))
    time.sleep(1.0)
    connector_client_02.close_connection()

    time.sleep(2.0)

    connector_message = ShikoniMessageRemoveConnector(message=[
        ShikoniMessageConnectorName().set_variables(True, "010"),
        ShikoniMessageConnectorName().set_variables(True, "011"),
    ])
    connector_base_client.send_message(connector_message)

    connector_base_client.close_connection()
    time.sleep(5.0)
    print()


if __name__ == '__main__':
    shikoni = ShikoniClasses(message_type_decode_file="data/massage_type_classes.json",
                             default_server_call_function=on_message)
    # TODO write start script

    args = sys.argv
    is_client = False
    server_port = 0
    if len(args) > 1:
        server_port = int(args[1])
    if len(args) > 2:
        if args[2] == "client":
            is_client = True

    if server_port > 0:
        if is_client:
            start_connection_message_test(shikoni, "127.0.0.1", server_port)
        else:
            start_base_shikoni_server(shikoni, server_port)
