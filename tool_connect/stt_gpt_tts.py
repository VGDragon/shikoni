import os
import pathlib
import time
import subprocess

from shikoni.ShikoniClasses import ShikoniClasses

from shikoni.tools.host_info import request_free_ports
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket

from shikoni.base_messages.ShikoniMessageAddConnectorGroup import ShikoniMessageAddConnectorGroup
from shikoni.base_messages.ShikoniMessageRemoveConnectorGroup import ShikoniMessageRemoveConnectorGroup

from shikoni.base_messages.ShikoniMessageAddConnectorToGroup import ShikoniMessageAddConnectorToGroup
from shikoni.message_types.ShikoniMessageRun import ShikoniMessageRun
from shikoni.message_types.ShikoniMessageClear import ShikoniMessageClear

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

    trigger_server_address = "127.0.0.1"
    trigger_port = 19994
    trigger_api_port = 19995
    trigger_server_name = "text trigger"

    gpt_server_address = "127.0.0.1"
    gpt_port = 19996
    gpt_api_port = 19997
    gpt_server_name = "gpt-3.5-turbo"

    shikoni = ShikoniClasses()
    # get base servers
    wisper_connector_base_client = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(wisper_server_address, wisper_port, False, "wisper", "/shikoni")
    )
    gpt_connector_base_client = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(gpt_server_address, gpt_port, False, "gpt", "/shikoni")
    )
    trigger_connector_base_client = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(trigger_server_address, trigger_port, False, "trigger", "/shikoni")
    )
    pyttsx3_connector_base_client = shikoni.start_client_connection(
        ShikoniMessageConnectorSocket().set_variables(pyttsx3_server_address, pyttsx3_port, False, "pyttsx3", "/shikoni")
    )
    # start server
    # wisper
    print("start server connectors")
    wisper_server_connector_port = request_free_ports(url=wisper_server_address, port=wisper_api_port, num_ports=1)[0]
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
    # trigger
    trigger_server_connector_port = request_free_ports(url=trigger_server_address, port=trigger_api_port, num_ports=1)[0]
    trigger_connector_base_client.send_message(
        ShikoniMessageAddConnectorGroup().set_variables(
            group_name=group_name_01,
            connector_socket_list=[
                ShikoniMessageConnectorSocket().set_variables(
                    url="0.0.0.0",
                    port=trigger_server_connector_port,
                    is_server=True,
                    connection_name=trigger_server_name)
            ]))
    # gpt
    gpt_server_connector_port = request_free_ports(url=gpt_server_address, port=gpt_api_port, num_ports=1)[0]
    gpt_connector_base_client.send_message(
        ShikoniMessageAddConnectorGroup().set_variables(
            group_name=group_name_01,
            connector_socket_list=[
                ShikoniMessageConnectorSocket().set_variables(
                    url="0.0.0.0",
                    port=gpt_server_connector_port,
                    is_server=True,
                    connection_name=gpt_server_name)
            ]))
    # pyttsx3
    pyttsx3_server_connector_port = request_free_ports(url=pyttsx3_server_address, port=pyttsx3_api_port, num_ports=1)[0]
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
                    url=trigger_server_address,
                    port=trigger_server_connector_port,
                    is_server=False,
                    connection_name=trigger_server_name)
            ]))
    # trigger
    trigger_connector_base_client.send_message(
        ShikoniMessageAddConnectorToGroup().set_variables(
            group_name=group_name_01,
            connector_socket_list=[
                ShikoniMessageConnectorSocket().set_variables(
                    url=gpt_server_address,
                    port=gpt_server_connector_port,
                    is_server=False,
                    connection_name=gpt_server_name)
            ]))
    # gpt
    gpt_connector_base_client.send_message(
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
    trigger_connector_base_client.send_message(
        ShikoniMessageRemoveConnectorGroup(group_name_01)
    )
    gpt_connector_base_client.send_message(
        ShikoniMessageRemoveConnectorGroup(group_name_01)
    )
    pyttsx3_connector_base_client.send_message(
        ShikoniMessageRemoveConnectorGroup(group_name_01)
    )

    wisper_connector_base_client.close_connection()
    trigger_connector_base_client.close_connection()
    gpt_connector_base_client.close_connection()
    pyttsx3_connector_base_client.close_connection()

    time.sleep(2.0)


def start_tools(is_windows: bool):  # TODO wrong pipenv used
    tools_to_start = [
        "shikoni_openai_wisper",
        "shikoni_text_trigger",
        "shikoni_gpt_api",
        "shikoni_pyttsx3",
    ]
    tools_processes = []
    for tool_folder_name in tools_to_start:
        tool_folder_dir = pathlib.Path(__file__).parent.parent.parent.joinpath(tool_folder_name)
        if is_windows:
            tool_start_script = str(tool_folder_dir.joinpath("start.bat"))
        else:
            tool_start_script = str(tool_folder_dir.joinpath("start.sh"))
        p = subprocess.Popen(tool_start_script, stdout=subprocess.PIPE, shell=True)
        tools_processes.append(p)
    time.sleep(2.0)
    return tools_processes


def stop_tools(tools_processes):
    for p in tools_processes:
        p.kill()
        p.terminate()


if __name__ == '__main__':
    tools_processes = start_tools(True)
    start_group_connection_message_test()
    stop_tools(tools_processes)
