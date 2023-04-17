import socket
import pickle
from maps import Map0
from player import Player
import pygame
from random import shuffle
import copy
import threading
import queue
from time import time, sleep

class Room(threading.Thread):
    def __init__(self, ip, udp_port, tcp_port, room_id):
        pygame.init()
        self.clock = pygame.time.Clock()
        threading.Thread.__init__(self)
        self.ip = ip
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind((ip, udp_port))
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.bind((ip, tcp_port))
        self.tcp.listen()

        self.room_id = room_id
        self.game_started = False
        self.map = None
        self.last_tag = 0
        self.cooldown = 1000
        self.is_restart = False

        self.player_sprite_paths = ['../assets/character/pirate_1/', '../assets/character/pirate_2/']
        shuffle(self.player_sprite_paths)
        self.is_tagged = [True, False]
        shuffle(self.is_tagged)
        self.current_player = 0
        self.set_player_variables = {
            'position': [(450, 450), (650, 450)],
            'direction': [0, 0],
            'facing_right': [True, True],
            'status': ['idle', 'idle'],
            'is_tagged': self.is_tagged,
            'frame_index': [0, 0]
        }
        self.player_variables = copy.deepcopy(self.set_player_variables)

        self.messages = queue.Queue()
        self.clients = []
        self.lock = threading.Lock()
        self.max_updates = 60
        self.last_update = time()

    def update_room(self, room_info):
        self.room_info = room_info
        print(self.room_info)

    def threaded_tcp(self, addr, connection):
        connection.sendall(pickle.dumps("Connected to room"))
        while True:
            try:
                data = connection.recv(2048)
                if not data:
                    print(addr,"left room", self.room_id)
                    break
                else:
                    data = pickle.loads(data)

                    if data['type'] == 'get_maps':
                        reply = [Map0()]

                    elif data['type'] == 'set_current_map':
                        self.map = int(data['map_no'])
                        reply = {'status': 1}

                    elif data['type'] == 'get_current_map':
                        if self.map is not None:
                            reply = {'status': 1, 'map': self.map}
                        else:
                            reply = {'status': 0}

                    elif data['type'] == 'start_game':
                        if self.room_info['room_leader'] == addr[0] and data['is_leader']:
                            self.game_started = True
                            reply = {'status': 1}
                        else:
                            if self.game_started:
                                reply = {'status': 1}
                            else:
                                reply = {'status': 0}

                    elif data['type'] == 'create_player':
                        player_no = self.room_info['player_room'].index(addr[0] + str(addr[1]))
                        self.room_info['player_objects'][addr[0] + str(addr[1])] = Player(0, self.player_variables['position'][player_no], self.player_variables['is_tagged'][player_no], self.player_sprite_paths.pop())
                        reply = {'status': 1, 'player': self.room_info['player_objects'][addr[0] + str(addr[1])]}

                    elif data['type'] == 'get_player':
                        players = []
                        for k in self.room_info['player_objects']:
                            if k != addr[0] + str(addr[1]):
                                players.append(self.room_info['player_objects'][k])

                        if len(players) != 0:
                            reply = {'status': 1, 'players': players}
                        else:
                            reply = {'status': 0}

                    elif data['type'] == 'ended':
                        reply = self.player_variables['is_tagged']
                        self.is_restart = False

                    elif data['type'] == 'is_restart':
                        reply = {'status': self.is_restart}

                    elif data['type'] == 'do_restart':
                        if self.room_info['room_leader'] == addr[0] and data['is_leader']:
                            self.is_restart = True
                            shuffle(self.set_player_variables['is_tagged'])
                            reply = {'status': 1}
                        else:
                            reply = {'status': 0}

                    elif data['type'] == 'reset':
                        self.player_variables = copy.deepcopy(self.set_player_variables)

                        player_no = self.room_info['player_room'].index(addr[0] + str(addr[1]))
                        if player_no == 0:
                            reply = self.player_variables
                        elif player_no == 1:
                            reply = {
                                'position': [self.player_variables['position'][1], self.player_variables['position'][0]],
                                'status': [self.player_variables['status'][1], self.player_variables['status'][0]],
                                'direction': [self.player_variables['direction'][1], self.player_variables['direction'][0]],
                                'facing_right': [self.player_variables['facing_right'][1], self.player_variables['facing_right'][0]],
                                'is_tagged': [self.player_variables['is_tagged'][1], self.player_variables['is_tagged'][0]]
                            }

                    else:
                        reply = "Invalid Request"

                    print(self.room_id, "IP:", addr, "received:", data)
                    print(self.room_id, "sending:", reply)

                    connection.sendall(pickle.dumps(reply))

            except Exception as e:
                print(e)

    def threaded_udp(self):
        while True:
            try:
                message, addr = self.udp.recvfrom(2048)
                self.messages.put((message, addr))
            except socket.timeout:
                pass

            while not self.messages.empty():
                message, addr = self.messages.get()
                data = pickle.loads(message)
                print(data)

                with self.lock:
                    if addr not in self.clients:
                        self.clients.append(addr)

                    if data['type'] == 'get_time':
                        reply = {
                            'cooldown': self.cooldown,
                            'current_time': pygame.time.get_ticks()
                        }

                        for client in self.clients:
                            try:
                                if client == addr:
                                    self.udp.sendto(pickle.dumps(reply), client)
                            except:
                                self.clients.remove(client)

                    elif data['type'] == 'update':
                        self.last_tag = data['last_tag']

                        player_no = self.room_info['players_udp'].index(data['username'])

                        for k,v in self.player_variables.items():
                            self.player_variables[k][player_no] = data[k]

                        if player_no == 0:
                            player_reply = 1
                        elif player_no == 1:
                            player_reply = 0

                        reply = {
                            'position': self.player_variables['position'][player_reply],
                            'direction': self.player_variables['direction'][player_reply],
                            'facing_right': self.player_variables['facing_right'][player_reply],
                            'status': self.player_variables['status'][player_reply],
                            'is_tagged': self.player_variables['is_tagged'][player_reply],
                            'frame_index': self.player_variables['frame_index'][player_reply]
                        }

                        for client in self.clients:
                            try:
                                if client == addr:
                                    current_time = time()
                                    since_last_update = current_time - self.last_update

                                    if since_last_update < 1.0 / self.max_updates:
                                        sleep((1.0 / self.max_updates) - since_last_update)
                                    self.last_update = time()
                                    self.udp.sendto(pickle.dumps(reply), client)
                            except:
                                self.clients.remove(client)

    def run(self):
        while True:
            connection, addr = self.tcp.accept()
            print(addr, "joined room", self.room_id)
            self.room_info['player_room'].append(addr[0] + str(addr[1]))
            threading.Thread(target=self.threaded_tcp, args=(addr, connection)).start()
            threading.Thread(target=self.threaded_udp).start()


class Server(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.start_server()

        self.connected_players = {}
        self.available_rooms = [str(i) for i in range(1, 11, 2)]
        self.active_rooms = {}

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen()
        print("Server started")

    def create_room(self, addr, room_id, username):
        self.active_rooms[room_id] = {
            'room': Room(self.ip, self.port+int(room_id), self.port+int(room_id)+1, room_id),
            'room_info': {
                'room_leader': addr[0],
                'players': [addr[0]],
                'player_objects': {},
                'player_room': [],
                'players_udp': [username]
            }
        }

        self.connected_players[addr[0]]['in_room'] = room_id
        self.active_rooms[room_id]['room'].update_room(self.active_rooms[room_id]['room_info'])

        while True:
            self.active_rooms[room_id]['room'].run()

    def threaded_create_room(self, addr, room_id, username):
        room_thread = threading.Thread(target=self.create_room, args=(addr, room_id, username))
        room_thread.start()

    def threaded_client(self, addr, connection):
        connection.sendall(pickle.dumps("Connected"))
        reply = ""
        while True:
            try:
                data = connection.recv(2048)
                if not data:
                    print("Disconnected:", addr)
                    break
                else:
                    data = pickle.loads(data)

                    if data['type'] == 'login':
                        self.connected_players[addr[0]] = {
                            'username': data['username']
                        }

                        reply = {'status': 1}

                    elif data['type'] == 'create_room':
                        room_id = self.available_rooms.pop()
                        self.threaded_create_room(addr, room_id, data['username'])

                        reply = {
                            'status': 1,
                            'udp_port': self.port + int(room_id),
                            'tcp_port': self.port + int(room_id) + 1
                        }

                    elif data['type'] == 'join_room':
                        room_id = data['room_id']
                        try:
                            self.connected_players[addr[0]]['in_room'] = room_id
                            self.active_rooms[room_id]['room_info']['players'].append(addr[0])
                            self.active_rooms[room_id]['room_info']['players_udp'].append(data['username'])
                            self.active_rooms[room_id]['room'].update_room(self.active_rooms[room_id]['room_info'])

                            print("Joined room")
                            print(self.active_rooms)
                            print(self.connected_players)

                            reply = {
                                'status': 1,
                                'udp_port': self.port + int(room_id),
                                'tcp_port': self.port + int(room_id) + 1
                            }

                        except KeyError:
                            reply = {'status': 0}

                    else:
                        reply = "Invalid"

                    print("Recieved: ", data)
                    print("Sending: ", reply)

                connection.sendall(pickle.dumps(reply))

            except Exception as e:
                print(e)

    def run(self):
        while True:
            connection, addr = self.server.accept()
            print("Connected to:", addr)

            server_thread = threading.Thread(target=self.threaded_client, args=(addr, connection))
            server_thread.start()

if __name__ == "__main__":
    ip = "10.30.203.91"
    port = 6000

    server = Server(ip, port)
    server.run()
