import socket
import pickle
from time import sleep

class Network:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = '127.0.0.1'
        self.server_port = 6000
        self.player = self.connect_server()

    def connect_server(self):
        try:
            self.server.connect((self.server_ip, self.server_port))
            return self.server.recv(2048)
        except Exception as e:
            print(e)

    def connect_tcp(self, tcp_port):
        try:
            self.tcp_client.connect((self.server_ip, tcp_port))
            return self.tcp_client.recv(2048)
        except Exception as e:
            print(e)

    def send_server(self, data):
        try:
            data = pickle.dumps(data)
            self.server.send(data)
            self.server.settimeout(10)
            response = pickle.loads(self.server.recv(2048))
            return response

        except socket.timeout:
            print("Server timed out")
        except socket.error as e:
            print(e)

    def send_tcp(self, data):
        try:
            data = pickle.dumps(data)
            self.tcp_client.send(data)
            self.tcp_client.settimeout(20)
            response = pickle.loads(self.tcp_client.recv(2048))
            return response

        except socket.timeout:
            print("Server timed out")
        except socket.error as e:
            print(e)

if __name__ == "__main__":
    n = Network()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 5010))
    print(pickle.loads(s.recv(2048)))
    s.send(pickle.dumps({'type': 'get_maps'}))
    print(pickle.loads(s.recv(2048)))
