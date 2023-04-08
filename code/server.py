import socket
from _thread import start_new_thread
import pickle
from maps import Map0
from player import Player
from random import shuffle

class Server():
    def __init__(self, ip, port):
        self.server = ip
        self.port = port
        self.start_server()

        # player
        self.current_player = 0
        self.player_positions = [(450, 450), (550, 450)]

    def start_server(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.server, self.port))
        self.s.listen()
        print("Server Started")

    def threaded_client(self, addr, connection, player):
        connection.send(pickle.dumps("Hehehehaw"))
        reply = ""
        while True:
            try:
                data = connection.recv(2048)
                if not data:
                    print("Disconnected:", addr)
                    break
                else:
                    data = pickle.loads(data)
                    if data['type'] == 'map_list':
                        reply = [Map0()]
                    elif data['type'] == 'get_id':
                        reply = player
                    elif data['type'] == 'create_player':
                        id = data['id']
                        reply = [Player(id, self.player_positions[id])]
                    else:
                        reply = data['sendme']

                    print("Recieved: ", data)
                    print("Sending: ", reply)

                connection.sendall(pickle.dumps(reply))

            except Exception as e:
                print(e)

        print("Connection Ended: ", addr)

    def run(self):
        while True:
            connection, addr = self.s.accept()
            print("Connected to:", addr)

            start_new_thread(self.threaded_client, (addr, connection, self.current_player))

            self.current_player += 1


if __name__ == "__main__":
    ip = "192.168.1.8"
    port = 8000

    server = Server(ip, port)
    server.run()
