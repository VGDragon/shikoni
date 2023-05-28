import time

from shikoni.ShikoniClasses import ShikoniClasses

from shikoni.tools.host_info import request_free_ports
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket

from shikoni.base_messages.ShikoniMessageAddConnectorGroup import ShikoniMessageAddConnectorGroup
from shikoni.base_messages.ShikoniMessageRemoveConnectorGroup import ShikoniMessageRemoveConnectorGroup

from shikoni.base_messages.ShikoniMessageAddConnectorToGroup import ShikoniMessageAddConnectorToGroup
from shikoni.message_types.ShikoniMessageRun import ShikoniMessageRun

def start_group_connection_message_test():
    base_server_port = 19980
    server_address = "127.0.0.1"

    group_name_01 = "base"

    wisper_server_address = "127.0.0.1"
    wisper_port = 19990
    wisper_api_port = 19991
    wisper_server_name = "get spoken text"

    pyttsx3_server_address = "127.0.0.1"
    pyttsx3_port = 19992
    pyttsx3_api_port = 19993
    pyttsx3_server_name = "text input"

    shikoni = ShikoniClasses()
    # get base servers
    wisper_connector_base_client = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, wisper_port, False, "wisper")
    )
    pyttsx3_connector_base_client = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(server_address, pyttsx3_port, False, "pyttsx3")
    )
    # connect to base server
    # wisper
    print("start server connectors")
    wisper_server_connector_port = request_free_ports(url=server_address, port=wisper_api_port, num_ports=1)[0]
    wisper_connector_base_client.send_message(
        ShikoniMessageAddConnectorGroup().set_variables(
            group_name=group_name_01,
            connector_socket_list=[
                ShikoniMessageConnectorSocket().set_variables(
                    url="0.0.0.0",
                    port=wisper_server_connector_port,
                    is_server=True,
                    connection_name=wisper_server_name)
            ]))
    # pyttsx3
    pyttsx3_server_connector_port = request_free_ports(url=server_address, port=pyttsx3_api_port, num_ports=1)[0]
    pyttsx3_connector_base_client.send_message(
        ShikoniMessageAddConnectorGroup().set_variables(
            group_name=group_name_01,
            connector_socket_list=[
                ShikoniMessageConnectorSocket().set_variables(
                    url="0.0.0.0",
                    port=pyttsx3_server_connector_port,
                    is_server=True,
                    connection_name=pyttsx3_server_name)
            ]))
    time.sleep(1.0)

    print("start client connectors")
    # connect clients to servers
    # wisper
    wisper_connector_base_client.send_message(
        ShikoniMessageAddConnectorToGroup().set_variables(
            group_name=group_name_01,
            connector_socket_list=[
                ShikoniMessageConnectorSocket().set_variables(
                    url=pyttsx3_server_address,
                    port=pyttsx3_server_connector_port,
                    is_server=False,
                    connection_name=pyttsx3_server_name)
            ]))
    # pyttsx3
    pyttsx3_connector_base_client.send_message(
        ShikoniMessageAddConnectorToGroup().set_variables(
            group_name=group_name_01,
            connector_socket_list=[
                ShikoniMessageConnectorSocket().set_variables(
                    url=wisper_server_address,
                    port=wisper_server_connector_port,
                    is_server=False,
                    connection_name=wisper_server_name)
            ]))
    print("start loop")
    connectio_to_start_loop = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(
                    url=wisper_server_address,
                    port=wisper_server_connector_port,
                    is_server=True,
                    connection_name="startup")
    )
    connectio_to_start_loop.send_message(
        ShikoniMessageRun()
    )
    connectio_to_start_loop.close_connection()

    time.sleep(120.0)

    print("close connectors")
    # close connections
    wisper_connector_base_client.send_message(
        ShikoniMessageRemoveConnectorGroup(group_name_01)
    )
    pyttsx3_connector_base_client.send_message(
        ShikoniMessageRemoveConnectorGroup(group_name_01)
    )

    pyttsx3_connector_base_client.close_connection()
    wisper_connector_base_client.close_connection()

    time.sleep(2.0)


if __name__ == '__main__':
    start_group_connection_message_test()
