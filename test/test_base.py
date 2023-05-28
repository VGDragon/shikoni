import pathlib
from unittest import main, TestCase
import time
import subprocess
import os
import json

from shikoni.tools.ShikoniInfo import start_shikoni_api
from shikoni.tools.host_info import request_free_ports
from shikoni.tools.host_info import find_free_ports

from shikoni.ShikoniClasses import ShikoniClasses
from shikoni.message_types.ShikoniMessageString import ShikoniMessageString
from shikoni.base_messages.ShikoniMessageAddConnector import ShikoniMessageAddConnector
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket
from shikoni.base_messages.ShikoniMessageRemoveConnector import ShikoniMessageRemoveConnector
from shikoni.base_messages.ShikoniMessageConnectorName import ShikoniMessageConnectorName
from shikoni.base_messages.ShikoniMessageAddConnectorGroup import ShikoniMessageAddConnectorGroup

output_file = "test_result.txt"

if os.path.exists(output_file):
    os.remove(output_file)


with open(output_file, "a") as f:
    f.write("[]")


class TestClass(TestCase):
    def tearDown(self):
        if hasattr(self._outcome, 'errors'):
            # Python 3.4 - 3.10  (These two methods have no side effects)
            result = self.defaultTestResult()
            self._feedErrorsToResult(result, self._outcome.errors)
        else:
            # Python 3.11+
            result = self._outcome.result
        ok = all(test != self for test, text in result.errors + result.failures)

        # Demo output:  (print short info immediately - not important)
        if ok:
            print('\nOK: %s' % (self.id(),))
        output_result = output_result = {"type": "OK"}
        for typ, errors in (('ERROR', result.errors), ('FAIL', result.failures)):
            for test, text in errors:
                if test is self:
                    # the full traceback is in the variable `text`
                    msg = [x for x in text.split('\n')[1:]
                           if not x.startswith(' ')][0]
                    text = "\n\n%s: %s\n     %s" % (typ, self.id(), msg)
                    print(text)
                    output_result = {"type": typ, "id": self.id(), "msg": msg}

        with open(output_file) as f:
            output_string = f.read()
        if len(output_string) > 2:
            output_string = "{0}, {1}]".format(output_string[:-1], json.dumps(output_result))
        else:
            output_string = "{0}{1}]".format(output_string[:-1], json.dumps(output_result))
        print(output_string)
        with open(output_file, "w") as f:
            f.write(output_string)


    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

    def test_start_base_server(self):
        ports = find_free_ports(num_ports=2)
        print(ports)

        shikoni = ShikoniClasses(default_server_call_function=on_message)
        shikoni.start_base_server_connection(
            ShikoniMessageConnectorSocket().set_variables(url="0.0.0.0",
                                                          port=ports[0],
                                                          is_server=True,
                                                          connection_name="001"),
            start_loop=False)
        api = start_shikoni_api(ports[1])
        time.sleep(5.0)
        shikoni.close_base_server()
        api.terminate()
        time.sleep(1.0)

    def test_open_server_on_base_server(self):
        ports = find_free_ports(num_ports=2)
        print(ports)

        shikoni = ShikoniClasses(default_server_call_function=on_message)
        shikoni.start_base_server_connection(
            ShikoniMessageConnectorSocket().set_variables(url="0.0.0.0",
                                                          port=ports[0],
                                                          is_server=True,
                                                          connection_name="001"),
            start_loop=False)
        shikoni.start_server_connections([
            ShikoniMessageConnectorSocket().set_variables("0.0.0.0", ports[1], True, "010")
        ])
        time.sleep(5.0)
        shikoni.close_server_connections(["010"])
        time.sleep(1.0)
        shikoni.close_base_server()
        time.sleep(1.0)

    def test_client_open_server_connection(self):
        # preparing
        test_server_ports = find_free_ports(num_ports=2)
        server_port = test_server_ports[0]
        api_server_port = test_server_ports[1]

        print(test_server_ports)
        server_address = "127.0.0.1"
        cmd = "python start_test_server.py {0} {1}".format(server_port, api_server_port)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        time.sleep(1.0)

        # testing
        shikoni = ShikoniClasses(default_server_call_function=on_message)
        # connect to base server
        connector_base_client = shikoni.start_client_connection(
            ShikoniMessageConnectorSocket().set_variables(server_address, server_port, False, "001")
        )

        server_ports = request_free_ports(url="127.0.0.1", port=api_server_port, num_ports=2)
        print(server_ports)

        # start new server connections with base server
        connector_message = ShikoniMessageAddConnector(message=[
            ShikoniMessageConnectorSocket().set_variables("0.0.0.0", server_ports[0], True, "010"),
            ShikoniMessageConnectorSocket().set_variables("0.0.0.0", server_ports[1], True, "011"),
            # ShikoniMessageConnectorSocket().set_variables(server_address, 19999, False, ""),
        ])
        connector_base_client.send_message(connector_message)
        time.sleep(2.0)

        # connect to the first new servers
        connector_client_01 = shikoni.start_client_connection(
            ShikoniMessageConnectorSocket().set_variables(server_address, server_ports[0], False, "002")
        )
        connector_client_01.send_message(ShikoniMessageString("Testing new server: 1"))
        time.sleep(1.0)
        connector_client_01.close_connection()

        # connect to the second new servers
        connector_client_02 = shikoni.start_client_connection(
            ShikoniMessageConnectorSocket().set_variables(server_address, server_ports[1], False, "003")
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
        time.sleep(2.0)
        p.kill()
        p.terminate()
        time.sleep(2.0)

    def test_client_open_server_group_connection(self):
        # preparing
        test_server_ports = find_free_ports(num_ports=2)
        server_port = test_server_ports[0]
        api_server_port = test_server_ports[1]
        group_name_01 = "101"
        group_name_02 = "102"
        control_file = pathlib.Path("server_group").joinpath("control_result.json")
        result_file = pathlib.Path("message.json")

        print(test_server_ports)
        server_address = "127.0.0.1"
        cmd = "python server_group/start_test_server_server_group.py {0} {1}".format(server_port, api_server_port)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        time.sleep(2.0)

        # testing
        shikoni = ShikoniClasses(default_server_call_function=on_message) # connect to base server

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
        print("open group connection 1")
        time.sleep(1.0)

        # start second server connection group
        connector_message = ShikoniMessageAddConnectorGroup().set_variables(
            group_name=group_name_02,
            connector_socket_list=[
                ShikoniMessageConnectorSocket().set_variables(server_address, free_port[0], False, "001"),
                ShikoniMessageConnectorSocket().set_variables(server_address, free_port[1], False, "002"),
                ShikoniMessageConnectorSocket().set_variables("0.0.0.0", free_port[2], True, "012")
            ])
        connector_base_client.send_message(connector_message)
        print("open group connection 2")
        time.sleep(1.0)

        # connect to the first new servers
        connector_client_01 = shikoni.start_client_connection(
            ShikoniMessageConnectorSocket().set_variables(server_address, free_port[2], False, "002")
        )
        connector_client_01.send_message(ShikoniMessageString("start"))
        time.sleep(2.0)
        connector_client_01.close_connection()

        connector_base_client.close_connection()
        time.sleep(2.0)
        p.kill()
        p.terminate()
        time.sleep(2.0)

        with open(control_file) as f:
            control_json = f.read()
        with open(result_file) as f:
            result_json = f.read()

        if control_json != result_json:
            print(result_json)
            raise Exception("result is wrong!!!")





def on_message(msg, shikoni):
    for key, item in msg.items():
        if isinstance(item, ShikoniMessageString):
            print(key, item.message)
        else:
            print(key, item)

if __name__ == "__main__":
    main()
