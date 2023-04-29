from multiprocessing import Process
from flask import Flask, request
from tools.host_info import find_free_ports
from flask import jsonify

class API:

    app = Flask(__name__)

    @app.route('/freeports')
    @staticmethod
    def hello():
        port_amount = 1
        if "num_ports" in request.args:
            port_amount = int(request.args.get("num_ports"))
        ports = find_free_ports(19985, 19990, port_amount)
        return jsonify(ports)


    def start_api(self, port):
        self.app.run(port=port, host="0.0.0.0")

def start_shikoni_api(port):
    api = API()
    api_process = Process(target=api.start_api, args=[port])
    api_process.start()
    return api_process

if __name__ == "__main__":
    start_shikoni_api(19989)
