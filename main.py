import sys
import time


from tools.PackageController import PackageController
from tools.ServerConnectorData import ConnectorSocket

from data.ShikoniClasses import ShikoniClasses
from message_types.ShikoniMessageString import ShikoniMessageString
from message_types.ShikoniMessageAddConnector import ShikoniMessageAddConnector
from message_types.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket


def on_message(msg):
    for key, item in msg.items():
        if isinstance(item, ShikoniMessageString):
            print(key, item.message)
        else:
            print(key, item)

def start_base_shikoni_server(shikoni: ShikoniClasses, server_port: int):
    shikoni.start_base_server_connection(
        ConnectorSocket(url="0.0.0.0", port=server_port, connection_name="001"))
    time.sleep(2.0)
    shikoni.close_base_server()
    shikoni.shutdown_manager()


def start_string_test_client(shikoni: ShikoniClasses, server_address: str, server_port: int):
    ShikoniMessageConnectorSocket().set_variables(server_address, server_port, False, "")

    connector_client_01 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, server_port, False, ""))
    connector_client_02 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, server_port + 1, False, "")
    )

    connector_client_01.send_message(ShikoniMessageString("Testing001: server 1"))  # TODO is sending to both clients
    time.sleep(0.1)
    connector_client_02.send_message(ShikoniMessageString("Testing001: server 2"))
    #connector_client_02.send_message(ShikoniMessageString(""))
    time.sleep(3.0)
    connector_client_01.send_message(ShikoniMessageString("Testing002: server 1"))
    time.sleep(0.1)
    connector_client_02.send_message(ShikoniMessageString("Testing002: server 2"))
    time.sleep(3.0)
    connector_client_01.close_connection()
    connector_client_02.close_connection()
    print()


def start_connection_message_test(shikoni: ShikoniClasses, server_address: str, server_port: int):
    # connect to base server
    connector_client_01 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, server_port, False, "")
    )

    # start new server connections with base server
    connector_message = ShikoniMessageAddConnector(message=[
        ShikoniMessageConnectorSocket().set_variables("0.0.0.0", 19980, True, "010"),
        ShikoniMessageConnectorSocket().set_variables("0.0.0.0", 19981, True, "011"),
        #ShikoniMessageConnectorSocket().set_variables(server_address, 19999, False, ""),
    ])
    connector_client_01.send_message(connector_message)  # TODO is sending to both clients
    time.sleep(2.0)
    connector_client_01.close_connection()

    # connect to the first new servers
    connector_client_01 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, 19980, False, "")
    )
    connector_client_01.send_message(ShikoniMessageString("Testing new server: 1"))
    time.sleep(1.0)
    connector_client_01.close_connection()

    # connect to the second new servers
    connector_client_01 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, 19981, False, "")
    )
    connector_client_01.send_message(ShikoniMessageString("Testing new server: 2"))
    time.sleep(1.0)
    connector_client_01.close_connection()

    time.sleep(10.0)
    print()

def message_encode_test(shikoni):

    connector_message_01 = ShikoniMessageAddConnector(message=[
        ShikoniMessageConnectorSocket().set_variables("0.0.0.0", 19980, True, "010"),
        ShikoniMessageConnectorSocket().set_variables("0.0.0.0", 19981, True, "011"),
        ShikoniMessageConnectorSocket().set_variables("127.0.0.1", 19999, False, ""),
    ])
    temp_01 = connector_message_01.encode()
    shikoni.encode_message(bytearray(temp_01))
    connector_message_02 = shikoni.encode_message(bytearray(temp_01))
    print()


if __name__ == '__main__':
    shikoni = ShikoniClasses(message_type_decode_file="data/massage_type_classes.json",
                             default_server_call_function=on_message)
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
            # start_string_test_client(shikoni, "127.0.0.1", server_port)
        else:
            start_base_shikoni_server(shikoni, server_port)
    #message_encode_test(shikoni)

    # message_example(shikoni)
    # test_package_install()
    #example()



