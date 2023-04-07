import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = '192.168.1.8'
        self.port = 5555
        self.player = self.connect()

    def get_player(self):
        return pickle.loads(self.player)

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
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)

if __name__ == "__main__":
    n = Network()
    print(n.send({'text': "Hello", 'sendme': 'GRRRRRRRR'}))
    print(n.send({'text': "World", 'sendme': 'grrrrrrrr'}))
    print(n.get_player())
