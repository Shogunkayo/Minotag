import socket
from _thread import start_new_thread
import pickle
from maps import Map0
from player import Player
import pygame

class Server():
    def __init__(self, ip, port):
        pygame.init()
        self.server = ip
        self.port = port
        self.start_server()

        # player
        self.current_player = 0
        self.player_variables = {
            'position': [(450, 450), (650, 450)],
            'direction': [1, 1],
            'facing_right': [True, True],
            'status': ['idle', 'idle']
        }
        self.players = []

    def start_server(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.server, self.port))
        self.s.listen()
        print("Server Started")

    def threaded_client(self, addr, connection, player):
        connection.sendall(pickle.dumps(self.players))
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
                        self.players.append(Player(id, self.player_variables['position'][id]))
                        if player == 0:
                            reply = self.players[0]
                        elif player == 1:
                            reply = self.players[1]

                    elif data['type'] == 'get_player':
                        if len(self.players) < 2:
                            reply = None
                        elif player == 0:
                            reply = self.players[1]
                        elif player == 1:
                            reply = self.players[0]

                    elif data['type'] == 'update':
                        if player == 0:
                            self.player_variables['position'][0] = data['position']
                            self.player_variables['direction'][0] = data['direction']
                            self.player_variables['facing_right'][0] = data['facing_right']
                            self.player_variables['status'][0] = data['status']

                            reply = {
                                'position': self.player_variables['position'][1],
                                'direction': self.player_variables['direction'][1],
                                'facing_right': self.player_variables['facing_right'][1],
                                'status': self.player_variables['status'][1]
                            }

                        elif player == 1:
                            self.player_variables['position'][1] = data['position']
                            self.player_variables['direction'][1] = data['direction']
                            self.player_variables['facing_right'][1] = data['facing_right']
                            self.player_variables['status'][1] = data['status']

                            reply = {
                                'position': self.player_variables['position'][0],
                                'direction': self.player_variables['direction'][0],
                                'facing_right': self.player_variables['facing_right'][0],
                                'status': self.player_variables['status'][0]
                            }

                    else:
                        reply = "Hehehehaw"

                    print(player, "Recieved: ", data)
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
