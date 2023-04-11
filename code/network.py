import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = '192.168.1.8'
        self.port = 8000
        self.player = self.connect()

    def connect(self):
        try:
            self.client.connect((self.ip, self.port))
            return self.client.recv(2048)
        except Exception as e:
            print(e)

    def send(self, data):
        try:
            data = pickle.dumps(data)
            self.client.send(data)
            self.client.settimeout(10)
            response = pickle.loads(self.client.recv(2048))
            return response

        except socket.timeout:
            print("Server timed out")
        except socket.error as e:
            print(e)

if __name__ == "__main__":
    n = Network()
    print(n.send({'type': "Hello", 'sendme': 'GRRRRRRRR'}))
    print(n.send({'type': "World", 'sendme': 'grrrrrrrr'}))
