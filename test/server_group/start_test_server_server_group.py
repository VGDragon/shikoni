import sys
import pathlib
import json

from shikoni.tools.ShikoniInfo import start_shikoni_api

from shikoni.ShikoniClasses import ShikoniClasses
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket
from shikoni.message_types.ShikoniMessageString import ShikoniMessageString


def on_message(msg, shikoni: ShikoniClasses):
    group_name = msg["group_name"]
    messages = msg["messages"]
    output_file = pathlib.Path("../message.json")
    print(msg)
    output_json = {"group_name": group_name, "messages": {}}
    for key, message in messages.items():
        output_json["messages"][key] = message.message

    ################

    with open(output_file) as f:
        output_string = f.read()
    if len(output_string) > 2:
        output_string = "{0}, {1}]".format(output_string[:-1], json.dumps(output_json))
    else:
        output_string = "{0}{1}]".format(output_string[:-1], json.dumps(output_json))
    print(output_string)
    with open(output_file, "w") as f:
        f.write(output_string)
    if group_name == "102":
        shikoni.send_to_all_clients(message=ShikoniMessageString("Testing"), group_name=group_name)


def start_base_shikoni_server(server_port: int, api_port: int):
    api_server = start_shikoni_api(api_port)
    shikoni.start_base_server_connection(
        connection_data=ShikoniMessageConnectorSocket().set_variables(url="0.0.0.0",
                                                                      port=server_port,
                                                                      is_server=True,
                                                                      connection_name="001"),
        start_loop=True
    )
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
        output_file = pathlib.Path("../message.json")
        with open(output_file, "w") as f:
            f.write("[]")
        start_base_shikoni_server(server_port, api_server_port)
