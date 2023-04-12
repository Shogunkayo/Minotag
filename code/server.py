import socket
import pickle
from maps import Map0
from player import Player
import pygame
from random import shuffle
import copy
import threading

class Room(threading.Thread):
    def __init__(self, ip, udp_port, tcp_port, room_id):
        threading.Thread.__init__(self)
        self.ip = ip
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind((ip, udp_port))
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.bind((ip, tcp_port))
        self.tcp.listen()

        self.room_id = room_id

    def update_room(self, room_info):
        self.room_info = room_info
        print(self.room_info)

    def threaded_tcp(self, addr, connection):
        connection.sendall(pickle.dumps("Connected"))
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

                    elif data['type'] == 'set_map':
                        self.map = int(data['map_no'])
                        reply = {'status': 1}

                    else:
                        reply = "Invalid Request"

                    print(self.room_id, "received:", data)
                    print(self.room_id, "sending:", reply)

                    connection.sendall(pickle.dumps(reply))

            except Exception as e:
                print(e)

    def run(self):
        while True:
            connection, addr = self.tcp.accept()
            print(addr, "joined room", self.room_id)
            threading.Thread(target=self.threaded_tcp, args=(addr, connection)).start()

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

    def create_room(self, addr, room_id):
        self.active_rooms[room_id] = {
            'room': Room(self.ip, self.port+int(room_id), self.port+int(room_id)+1, room_id),
            'room_info': {
                'room_leader': addr[0],
                'players': [addr[0]]
            }
        }

        self.connected_players[addr[0]]['in_room'] = room_id
        self.active_rooms[room_id]['room'].update_room(self.active_rooms[room_id]['room_info'])

        while True:
            self.active_rooms[room_id]['room'].run()

    def threaded_create_room(self, addr, room_id):
        room_thread = threading.Thread(target=self.create_room, args=(addr, room_id))
        room_thread.start()

    def threaded_client(self, addr, connection):
        connection.sendall(pickle.dumps("Connected"))
        reply = ""
        while True:
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
                        self.threaded_create_room(addr, room_id)

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
                        reply = "Invalid Request"

                    print("Recieved: ", data)
                    print("Sending: ", reply)

                connection.sendall(pickle.dumps(reply))

                if data['type'] in ['join_room', 'create_room'] and reply['status'] == 1:
                    print("Disconnected:", addr)
                    break

    def run(self):
        while True:
            connection, addr = self.server.accept()
            print("Connected to:", addr)

            server_thread = threading.Thread(target=self.threaded_client, args=(addr, connection))
            server_thread.start()

if __name__ == "__main__":
    ip = "192.168.1.8"
    port = 4000

    server = Server(ip, port)
    server.run()
