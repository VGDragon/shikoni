import socket
import requests
import json

def find_free_ports(num_ports=None):
    """Finds free ports within the given range and returns them as a list."""
    ports = []
    if num_ports is None:
        num_ports = 1
    for port in range(num_ports):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', 0))
                ports.append(s.getsockname()[1])
                s.close()
            except OSError:
                pass
    return ports  # TODO port can't be used sometimes

def request_free_ports(url: str, port: int, num_ports: int = 1):
    if not url.startswith("http://"):
        url = "http://{0}".format(url)
    r = requests.get(url="{0}:{1}/freeports".format(url, port), params={"num_ports": str(num_ports)})
    return json.loads(r.text)

if __name__ == "__main__":
    r = request_free_ports("127.0.0.1", 19989, 2)
    print(r)
