import socket
from _thread import start_new_thread
import pickle

class Server():
    def __init__(self, ip, port):
        self.server = ip
        self.port = port
        self.start_server()
        self.players = []
        self.current_player = 0

    def start_server(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.server, self.port))
        self.s.listen()
        print("Server Started")

    def threaded_client(self, connection, player):
        connection.send(pickle.dumps("Hehehehaw"))

        reply = ""
        while True:
            try:
                data = connection.recv(2048)

                if not data:
                    print("Disconnected")
                    break
                else:
                    data = pickle.loads(data)
                    reply = data['sendme']

                    print("Recieved: ", data['text'])
                    print("Sending: ", reply)

                connection.sendall(pickle.dumps(reply))

            except Exception as e:
                print(e)

        print("Connection Ended")

    def run(self):
        while True:
            connection, addr = self.s.accept()
            print("Connected to:", addr)

            start_new_thread(self.threaded_client, (connection,
                                                    self.current_player))

            self.current_player += 1


if __name__ == "__main__":
    ip = "192.168.1.8"
    port = 5555

    server = Server(ip, port)
    server.run()
