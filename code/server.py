import socket
from _thread import start_new_thread
import pickle
from maps import Map0
from player import Player
import pygame
from random import shuffle
import copy

class Room():
    def __init__(self, id):
        pygame.init()
        self.id = id
        self.current_player = 0
        self.last_tag = 0
        self.cooldown = 1000

        self.is_tagged = [True, False]
        shuffle(self.is_tagged)
        self.current_player = 0
        self.player_variables = {
            'position': [(450, 450), (650, 450)],
            'direction': [0, 0],
            'facing_right': [True, True],
            'status': ['idle', 'idle'],
            'is_tagged': self.is_tagged
        }
        self.set_player_variables = self.player_variables.copy()
        self.players = []

        def create_player(self, data, player):
            id = data['id']
            reply = ''
            self.players.append(Player(id, self.player_variables['position'][player],self.player_variables['is_tagged'][player]))
            if player == 0:
                reply = self.players[0]
            elif player == 1:
                reply = self.players[1]

            return reply

        def get_player(self, data, player):
            if len(self.players) < 2:
                reply = None
            elif player == 0:
                reply = self.players[1]
            elif player == 1:
                reply = self.players[0]

            return reply

class Server():
    def __init__(self, ip, port):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.last_tag = 0
        self.cooldown = 1500
        self.server = ip
        self.port = port
        self.start_server()

        # player
        self.player_sprite_paths = ['../assets/character/pirate_1/', '../assets/character/pirate_2/', '../assets/character/pirate_3']
        shuffle(self.player_sprite_paths)
        self.is_tagged = [True, False]
        shuffle(self.is_tagged)
        self.current_player = 0
        self.set_player_variables = {
            'position': [(450, 450), (650, 450)],
            'direction': [0, 0],
            'facing_right': [True, True],
            'status': ['idle', 'idle'],
            'is_tagged': self.is_tagged
        }
        self.player_variables = copy.deepcopy(self.set_player_variables)
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
                        self.players.append(Player(id, self.player_variables['position'][player],self.player_variables['is_tagged'][player], self.player_sprite_paths.pop()))
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
                        self.last_tag = data['last_tag']

                        if player == 0:
                            self.player_variables['position'][0] = data['position']
                            self.player_variables['direction'][0] = data['direction']
                            self.player_variables['facing_right'][0] = data['facing_right']
                            self.player_variables['status'][0] = data['status']
                            self.player_variables['is_tagged'][0] = data['is_tagged']

                            reply = {
                                'position': self.player_variables['position'][1],
                                'direction': self.player_variables['direction'][1],
                                'facing_right': self.player_variables['facing_right'][1],
                                'status': self.player_variables['status'][1],
                                'is_tagged': self.player_variables['is_tagged'][1]
                            }

                        elif player == 1:
                            self.player_variables['position'][1] = data['position']
                            self.player_variables['direction'][1] = data['direction']
                            self.player_variables['facing_right'][1] = data['facing_right']
                            self.player_variables['status'][1] = data['status']
                            self.player_variables['is_tagged'][1] = data['is_tagged']

                            reply = {
                                'position': self.player_variables['position'][0],
                                'direction': self.player_variables['direction'][0],
                                'facing_right': self.player_variables['facing_right'][0],
                                'status': self.player_variables['status'][0],
                                'is_tagged': self.player_variables['is_tagged'][0]
                            }

                    elif data['type'] == 'get_time':
                        reply = {
                            'cooldown': self.cooldown,
                            'current_time': pygame.time.get_ticks()
                        }

                    elif data['type'] == 'ended':
                        reply = self.player_variables['is_tagged']

                    elif data['type'] == 'reset':
                        self.player_variables = copy.deepcopy(self.set_player_variables)
                        print("\n\n\n\n", self.set_player_variables, "\n\n\n\n")
                        if player == 0:
                            reply = self.player_variables
                        elif player == 1:
                            reply = {
                                'position': [self.player_variables['position'][1], self.player_variables['position'][0]],
                                'status': [self.player_variables['status'][1], self.player_variables['status'][0]],
                                'direction': [self.player_variables['direction'][1], self.player_variables['direction'][0]],
                                'facing_right': [self.player_variables['facing_right'][1], self.player_variables['facing_right'][0]],
                                'is_tagged': [self.player_variables['is_tagged'][1], self.player_variables['is_tagged'][0]]
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
    ip = "10.30.204.36"
    port = 8000

    server = Server(ip, port)
    server.run()
