import sys
import time


from tools.PackageController import PackageController

from data.ShikoniClasses import ShikoniClasses
from message_types.ShikoniMessageString import ShikoniMessageString


def start_shikoni_server(shikoni: ShikoniClasses, server_port: int):

    server_01 = shikoni.start_server_connection("0.0.0.0", server_port, on_message)
    time.sleep(100.0)
    shikoni.close_server(server_01)
    print()

def on_message(msg):
    print(msg.message)


def start_test_client(shikoni: ShikoniClasses, server_address: str,  server_port: int):
    connector_client_01 = shikoni.start_client_connection(server_address, server_port)

    connector_client_01.send_message(ShikoniMessageString("Testing009: server 1"))
    #connector_client_02.send_message(ShikoniMessageString(""))
    time.sleep(3.0)
    connector_client_01.send_message(ShikoniMessageString("Testing009: server 1"))
    time.sleep(3.0)
    connector_client_01.close_client_connection()
    print()

def test_package_install():
    pc = PackageController()
    temp_002 = pc.get_module_class("message_types.MessageTTS", "MessageTTS").decode_message()
    print()

if __name__ == '__main__':
    shikoni = ShikoniClasses("data/massage_type_classes.json")
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
            start_test_client(shikoni, "127.0.0.1", server_port)
        else:
            start_shikoni_server(shikoni, server_port)

    # message_example(shikoni)
    # test_package_install()
    #example()



