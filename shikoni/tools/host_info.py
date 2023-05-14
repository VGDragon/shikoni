import socket
import requests
import json

def find_free_ports(start_port=None, end_port=None, num_ports=None):
    """Finds free ports within the given range and returns them as a list."""
    ports = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        base_port = s.getsockname()[1]
    if start_port is None:
        start_port = base_port
    if end_port is None:
        end_port = 65500
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                ports.append(port)
            except OSError:
                pass
            if num_ports is not None and len(ports) >= num_ports:
                break
    return ports[:num_ports] if num_ports else ports[:1]  # TODO port can't be used sometimes

def request_free_ports(url: str, port: int, num_ports: int = 1):
    if not url.startswith("http://"):
        url = "http://{0}".format(url)
    r = requests.get(url="{0}:{1}/freeports".format(url, port), params={"num_ports": str(num_ports)})
    return json.loads(r.text)

if __name__ == "__main__":
    r = request_free_ports("127.0.0.1", 19989, 2)
    print(r)
