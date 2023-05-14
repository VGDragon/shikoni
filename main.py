import sys
import time

from shikoni.ShikoniClasses import ShikoniClasses

from shikoni.tools.ShikoniInfo import start_shikoni_api
from shikoni.tools.host_info import request_free_ports
from shikoni.tools.host_info import find_free_ports

from shikoni.message_types.ShikoniMessageString import ShikoniMessageString
from shikoni.base_messages.ShikoniMessageAddConnector import ShikoniMessageAddConnector
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket
from shikoni.base_messages.ShikoniMessageRemoveConnector import ShikoniMessageRemoveConnector
from shikoni.base_messages.ShikoniMessageConnectorName import ShikoniMessageConnectorName

from shikoni.base_messages.ShikoniMessageAddConnectorGroup import ShikoniMessageAddConnectorGroup
from shikoni.base_messages.ShikoniMessageRemoveConnectorGroup import ShikoniMessageRemoveConnectorGroup

from shikoni.base_messages.ShikoniMessageAddConnectorToGroup import ShikoniMessageAddConnectorToGroup


def on_message(msg):
    print(msg)


def on_message_client_test(msg):
    print(msg)


def start_base_shikoni_server(shikoni: ShikoniClasses, server_port: int, join_server: bool = True):
    api_server = start_shikoni_api(server_port + 1)
    shikoni.start_base_server_connection(
        connection_data=ShikoniMessageConnectorSocket().set_variables(url="0.0.0.0",
                                                                      port=server_port,
                                                                      is_server=True,
                                                                      connection_name="001"),
        start_loop=join_server
    )
    time.sleep(20.0)
    shikoni.close_base_server()
    api_server.terminate()


def start_connection_message_test(shikoni: ShikoniClasses, server_address: str, server_port: int):
    # connect to base server
    connector_base_client = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, server_port, False, "001")
    )
    free_port = request_free_ports(url=server_address, port=server_port + 1, num_ports=2)
    # start new server connections with base server
    connector_message = ShikoniMessageAddConnector(message=[
        ShikoniMessageConnectorSocket().set_variables("0.0.0.0", free_port[0], True, "010"),
        ShikoniMessageConnectorSocket().set_variables("0.0.0.0", free_port[1], True, "011"),
        # ShikoniMessageConnectorSocket().set_variables(server_address, 19999, False, ""),
    ])
    connector_base_client.send_message(connector_message)
    time.sleep(2.0)

    # connect to the first new servers
    connector_client_01 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, free_port[0], False, "002")
    )
    connector_client_01.send_message(ShikoniMessageString("Testing new server: 1"))
    time.sleep(1.0)
    connector_client_01.close_connection()

    # connect to the second new servers
    connector_client_02 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, free_port[1], False, "003")
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


def start_group_connection_message_test(shikoni: ShikoniClasses, server_address: str, server_port: int):
    group_name_01 = "101"
    group_name_02 = "102"

    # connect to base server
    connector_base_client = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, server_port, False, "001")
    )

    free_port = request_free_ports(url=server_address, port=server_port + 1, num_ports=4)
    print(free_port)

    # start first server connection group
    connector_message = ShikoniMessageAddConnectorGroup().set_variables(
        group_name=group_name_01,
        connector_socket_list=[
            ShikoniMessageConnectorSocket().set_variables("0.0.0.0", free_port[0], True, "010"),
            ShikoniMessageConnectorSocket().set_variables("0.0.0.0", free_port[1], True, "011"),
            # ShikoniMessageConnectorSocket().set_variables(server_address, free_port[2], False, ""),
        ])
    connector_base_client.send_message(connector_message)
    time.sleep(2.0)

    # start second server connection group
    connector_message = ShikoniMessageAddConnectorGroup().set_variables(
        group_name=group_name_02,
        connector_socket_list=[
            ShikoniMessageConnectorSocket().set_variables(server_address, free_port[0], False, ""),
            ShikoniMessageConnectorSocket().set_variables(server_address, free_port[1], False, ""),
            ShikoniMessageConnectorSocket().set_variables("0.0.0.0", free_port[2], True, "012")
        ])
    connector_base_client.send_message(connector_message)
    time.sleep(2.0)

    # add client to first server connection group
    #connector_message = ShikoniMessageAddConnectorToGroup().set_variables(
    #    group_name=group_name_01,
    #    connector_socket_list=[
    #        ShikoniMessageConnectorSocket().set_variables(server_address, free_port[2], False, ""),
    #    ])
    #connector_base_client.send_message(connector_message)
    #time.sleep(2.0)

    ##############################################################

    # connect to the first new servers
    connector_client_01 = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, free_port[2], False, "002")
    )
    connector_client_01.send_message(ShikoniMessageString("start"))
    time.sleep(1.0)
    connector_client_01.close_connection()


    ##############################################################

    connector_base_client.close_connection()
    time.sleep(5.0)
    print()


if __name__ == '__main__':
    shikoni = ShikoniClasses(message_type_decode_file="shikoni/data/massage_type_classes.json",
                             default_server_call_function=on_message)
    # TODO make it save - API key?
    # TODO find minimum package versions - DONE ???
    # TODO add connection group test

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
            # start_group_connection_message_test(shikoni, "127.0.0.1", server_port)
        else:
            start_base_shikoni_server(shikoni, server_port)
