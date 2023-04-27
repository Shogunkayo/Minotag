import socket
import pickle
from maps import BaseMap
from player import Player
import pygame
from random import shuffle, choices
from string import ascii_lowercase, digits
import copy
import threading
import queue
from time import time, sleep
import psycopg2
import psycopg2.pool
from dotenv import load_dotenv
import os
import bcrypt

class Room(threading.Thread):
    def __init__(self, ip, udp_port, tcp_port, room_id):
        pygame.init()
        self.clock = pygame.time.Clock()
        threading.Thread.__init__(self)
        self.ip = ip
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp.bind((ip, udp_port))
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp.bind((ip, tcp_port))
        self.tcp.settimeout(5)
        self.tcp.listen()

        self.room_id = room_id
        self.game_started = False
        self.map = None
        self.last_tag = 0
        self.cooldown = 1000
        self.set_timer = 10
        self.timer = self.set_timer
        self.timer_cooldown = 0
        self.is_restart = False

        self.set_player_sprite_paths = ['../assets/character/pirate_1/', '../assets/character/pirate_2/', '../assets/character/pirate_3/']
        shuffle(self.set_player_sprite_paths)
        self.player_sprite_paths = self.set_player_sprite_paths.copy()

        self.is_tagged = [True]
        self.current_map_no = 0
        self.set_player_variables = {
            'pos': [(450, 450), (650, 450), (550, 450)],
            'direction': [0, 0, 0],
            'facing_right': [True, True, True],
            'status': ['idle', 'idle', 'idle'],
            'is_tagged': self.is_tagged,
            'frame_index': [0, 0, 0]
        }
        self.player_variables = copy.deepcopy(self.set_player_variables)
        self.variables_reset = False

        self.available_spots = []
        self.tcp_clients = []

        self.messages = queue.Queue()
        self.clients = []
        self.lock = threading.Lock()
        self.max_updates = 60
        self.last_update = time()

        self.room_close = False

    def update_room(self, room_info):
        self.room_info = room_info
        print("UPDATED ROOM IN ROOM", self.room_info)

    def threaded_tcp(self, addr, tcp_connection, chat_connection):
        tcp_connection.sendall(pickle.dumps("Connected to room"))
        chat_connection.sendall(pickle.dumps("Connected to chat"))
        while True:
            try:
                data = tcp_connection.recv(2048)
                if not data:
                    print(addr,"left room", self.room_id)
                    print("\n\n\n", self.room_info, "\n\n\n")
                    break
                else:
                    data = pickle.loads(data)
                    if data['type'] == 'chat' and data['message']:
                        if data['username'] and data['token'] and self.room_info['players'][data['username']]:
                            if self.room_info['players'][data['username']]['token'] == data['token']:
                                print("Room", self.room_id, "received from IP:", data, "\n\n")
                                reply = {
                                    'status': 1,
                                    'type': 'chat',
                                    'message': data['message'],
                                    'username': data['username']
                                }
                                for client in self.tcp_clients:
                                    client.sendall(pickle.dumps(reply))
                                tcp_connection.sendall(pickle.dumps(reply))
                            else:
                                reply = {
                                    'status': 0,
                                    'message': "Unauthorized request"
                                }
                                chat_connection.sendall(pickle.dumps(reply))
                                tcp_connection.sendall(pickle.dumps(reply))
                        else:
                            chat_connection.sendall({pickle.dumps({
                                'status': 0,
                                'message': "Malformed request"
                            })})
                            tcp_connection.sendall({pickle.dumps({
                                'status': 0,
                                'message': "Malformed request"
                            })})
                    else:
                        if data['username'] and data['token'] and self.room_info['players'][data['username']]:
                            if self.room_info['players'][data['username']]['token'] == data['token']:
                                if data['type'] == 'player_init':
                                    sprite_path = self.player_sprite_paths.pop()
                                    self.room_info['players'][data['username']]['player_sprite'] = sprite_path
                                    self.available_spots.append(data['username'])
                                    reply = {
                                        'status': 1,
                                        'map_list': [(0, BaseMap('map0')), (1, BaseMap('map1'))],
                                        'player_sprite': sprite_path
                                    }

                                elif data['type'] == 'ready':
                                    self.room_info['players'][data['username']]['ready'] = True
                                    reply = {
                                        'status': 1
                                    }

                                elif data['type'] == 'unready':
                                    if not self.game_started:
                                        self.room_info['players'][data['username']]['ready'] = False
                                        reply = {
                                            'status': 1
                                        }
                                    else:
                                        reply = {
                                            'status': 0,
                                            'message': "Game started"
                                        }

                                elif data['type'] == 'get_ready':
                                    if self.room_info['room_leader'] == data['username']:
                                        self.current_map_no = data['current_map_no']

                                    players = {}
                                    for i in self.room_info['players']:
                                        temp = self.room_info['players'][i].copy()
                                        del temp['token']
                                        del temp['player_object']
                                        del temp['ip']
                                        players[i] = temp

                                    reply = {
                                        'status': 1,
                                        'players': players,
                                        'current_map_no': self.current_map_no,
                                        'room_leader': self.room_info['room_leader'],
                                        'game_started': self.game_started
                                    }

                                elif data['type'] == 'exit_room_lobby':
                                    self.player_sprite_paths.append(self.room_info['players'][data['username']]['player_sprite'])
                                    del self.room_info['players'][data['username']]
                                    self.available_spots.remove(data['username'])

                                    if len(self.available_spots) > 0:
                                        for username in self.room_info['players']:
                                            self.room_info['players'][username]['player_no'] = self.available_spots.index(username)
                                        if self.room_info['room_leader'] == data['username']:
                                            self.room_info['room_leader'] = self.available_spots[0]
                                            self.room_info['players'][self.available_spots[0]]['ready'] = True
                                    else:
                                        self.room_close = True

                                    print("ROOM ROOM INFO:", self.room_info)

                                    reply = {
                                        'status': 1
                                    }

                                elif data['type'] == 'start_game':
                                    if data['username'] == self.room_info['room_leader']:
                                        all_ready = True
                                        for username, player in self.room_info['players'].items():
                                            if not player['ready']:
                                                all_ready = False
                                                break

                                        if all_ready:
                                            self.game_started = True
                                            self.timer = self.set_timer
                                            if self.variables_reset:
                                                self.player_variables = copy.deepcopy(self.set_player_variables)
                                                self.variables_reset = False
                                            is_tagged = [True]
                                            for _ in range(1, len(self.available_spots)):
                                                is_tagged.append(False)
                                            shuffle(is_tagged)
                                            self.player_variables['is_tagged'] = is_tagged

                                            reply = {
                                                'status': 1,
                                            }
                                        else:
                                            reply = {
                                                'status': 0,
                                                'message': "Unready players"
                                            }
                                    else:
                                        reply = {
                                            'status': 0,
                                            'message': "Only the room leader can start"
                                        }

                                elif data['type'] == 'create_player':
                                    player_no = self.room_info['players'][data['username']]['player_no']
                                    player = Player(self.player_variables['pos'][player_no], self.player_variables['is_tagged'][player_no], self.room_info['players'][data['username']]['player_sprite'])
                                    self.room_info['players'][data['username']]['player_object'] = player

                                    reply = {
                                        'status': 1,
                                        'player_object': player
                                    }

                                elif data['type'] == 'player_loaded':
                                    self.room_info['players'][data['username']]['player_loaded'] = True

                                    reply = {
                                        'status': 1
                                    }

                                elif data['type'] == 'check_start':
                                    all_loaded = True
                                    for username, player in self.room_info['players'].items():
                                        if not player['player_loaded']:
                                            all_loaded = False

                                    if all_loaded:
                                        reply = {
                                            'status': 1,
                                        }

                                    else:
                                        reply = {
                                            'status': 0,
                                            'message': "Not all players have loaded"
                                        }

                                elif data['type'] == 'load_others':
                                    other_players = {}
                                    for username, player in self.room_info['players'].items():
                                        if username != data['username']:
                                            other_players[username] = {
                                                'player_object': player['player_object']
                                            }

                                    reply = {
                                        'status': 1,
                                        'other_players': other_players
                                    }

                                elif data['type'] == 'game_ended':
                                    if self.room_info['room_leader'] == data['username']:
                                        for username, player in self.room_info['players'].items():
                                            if username != self.room_info['room_leader']:
                                                player['ready'] = False
                                            player['player_loaded'] = False
                                        shuffle(self.set_player_variables['is_tagged'])
                                        self.variables_reset = True

                                    for username, player in self.room_info['players'].items():
                                        if self.player_variables['is_tagged'][player['player_no']]:
                                            reply = {
                                                'status': 1,
                                                'username': username,
                                                'player_sprite': player['player_sprite']
                                            }
                                            break

                                else:
                                    reply = {
                                        'status': 0,
                                        'message': "Invalid request"
                                    }

                            else:
                                reply = {
                                    'status': 0,
                                    'message': "Unauthorized request"
                                }
                        else:
                            reply = {
                                'status': 0,
                                'message': "Malformed request"
                            }

                        print("Room", self.room_id, "received from IP:", addr, data)
                        print("Room", self.room_id, "sending:", reply, "\n\n")

                        tcp_connection.sendall(pickle.dumps(reply))

                    if data['type'] == 'exit_room_lobby':
                        print("TCP THREAD CLOSED")
                        return
            except KeyError:
                reply = {
                    'status': 0,
                    'message': "Malformed request"
                }
                tcp_connection.sendall(pickle.dumps(reply))

            except Exception as e:
                print("Server error:", e)
                reply = {
                    'status': 0,
                    'message': "Server error"
                }
                tcp_connection.sendall(pickle.dumps(reply))

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
                        current_time = pygame.time.get_ticks()
                        if current_time - self.timer_cooldown > 1000:
                            self.timer_cooldown = current_time
                            self.timer -= 1

                        reply = {
                            'cooldown': self.cooldown,
                            'current_time': current_time,
                            'timer': self.timer
                        }

                        if self.timer <= 0:
                            self.game_ended = True
                            self.game_started = False

                        for client in self.clients:
                            try:
                                if client == addr:
                                    self.udp.sendto(pickle.dumps(reply), client)
                            except:
                                self.clients.remove(client)

                    elif data['type'] == 'update':
                        try:
                            if data['username'] and data['token']:
                                if self.room_info['players'][data['username']]['token'] == data['token']:
                                    self.last_tag = data['last_tag']

                                    player_no = self.room_info['players'][data['username']]['player_no']
                                    for k,v in self.player_variables.items():
                                        self.player_variables[k][player_no] = data[k]

                                    reply = {}
                                    for username, player in self.room_info['players'].items():
                                        if username != data['username']:
                                            reply[username] = {
                                                'pos': self.player_variables['pos'][player['player_no']],
                                                'direction': self.player_variables['direction'][player['player_no']],
                                                'facing_right': self.player_variables['facing_right'][player['player_no']],
                                                'status': self.player_variables['status'][player['player_no']],
                                                'is_tagged': self.player_variables['is_tagged'][player['player_no']],
                                                'frame_index': self.player_variables['frame_index'][player['player_no']]
                                            }
                                else:
                                    reply = {
                                        'status': 0,
                                        'message': "Unauthorized request",
                                    }
                        except KeyError:
                            reply = {
                                'status': 0,
                                'message': "Invalid request"
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

                    elif data['type'] == 'exit_room_lobby':
                        reply = {
                            'status': 1
                        }
                        for client in self.clients:
                            try:
                                if client == addr:
                                    self.udp.sendto(pickle.dumps(reply), client)
                            except:
                                self.clients.remove(client)
                        print("UDP THREAD CLOSED")
                        return

    def run(self):
        if self.room_close:
            return
        try:
            tcp_connection, addr = self.tcp.accept()
            chat_connection, addr = self.tcp.accept()
            self.tcp_clients.append(chat_connection)
            print(addr, "joined room", self.room_id)
            threading.Thread(target=self.threaded_tcp, args=(addr, tcp_connection, chat_connection)).start()
            threading.Thread(target=self.threaded_udp).start()
        except socket.timeout:
            pass
        except Exception as e:
            print(e)

class Server(threading.Thread):
    def __init__(self, ip, port, pool):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.start_server()
        self.pool = pool

        self.connected_players = {}
        self.available_rooms = [{
            'room_no': str(i),
            'room_id': ''.join(choices(ascii_lowercase + digits, k=5))
        } for i in range(1, 11, 2)]
        self.active_rooms = {}

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen()
        print("Server started")

    def create_room(self, addr, room_id, username, token):
        self.active_rooms[room_id['room_no']]['data'] = {
            'room_object': Room(self.ip, self.port+int(room_id['room_no']), self.port+int(room_id['room_no'])+1, room_id['room_no']),
            'room_id': room_id['room_id'],
            'room_info': {
                'room_leader': username,
                'current_map': None,
                'players': {
                    username: {
                        'ip': addr[0],
                        'username': username,
                        'token': token,
                        'player_object': None,
                        'player_no': 0,
                        'ready': True,
                        'player_sprite': None,
                        'player_loaded': False
                    }
                }
            }
        }

        self.connected_players[username]['in_room'] = room_id
        self.active_rooms[room_id['room_no']]['data']['room_object'].update_room(self.active_rooms[room_id['room_no']]['data']['room_info'])

        while True:
            try:
                self.active_rooms[room_id['room_no']]['data']['room_object'].run()
            except KeyError:
                return

    def threaded_create_room(self, addr, room_id, username, token):
        print("Created Room")
        self.active_rooms[room_id['room_no']] = {}
        print(self.active_rooms, "\n\n")
        print(self.available_rooms, "\n\n")
        room_thread = threading.Thread(target=self.create_room, args=(addr, room_id, username, token))
        self.active_rooms[room_id['room_no']]['thread'] = room_thread
        room_thread.start()

    def threaded_client(self, addr, connection, db_conn):
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
                        if data['username'] and data['password']:
                            data['username'] = str(data['username'])
                            data['password'] = str(data['password'])

                            cur = db_conn.cursor()
                            cur.execute("SELECT password FROM users WHERE username = (%s)", (data['username'], ))
                            res = cur.fetchone()
                            cur.close()
                            if res is not None:
                                hash = res[0].tobytes()
                                if bcrypt.checkpw(data['password'].encode(), hash):
                                    token = str(1000 + len(self.connected_players))
                                    self.connected_players[data['username']] = {
                                        'username': data['username'],
                                        'token': token,
                                        'ip': addr[0],
                                        'in_room': False
                                    }

                                    reply = {
                                        'status': 1,
                                        'token': token,
                                        'hehe': 'hehaw'
                                    }
                                else:
                                    reply = {
                                        'status': 0,
                                        'message': 'Username or Password is incorrect',
                                        'error_code': 403
                                    }
                            else:
                                reply = {
                                    'status': 0,
                                    'message': "User does not exist",
                                    'error_code': 401
                                }
                        else:
                            reply = {
                                'status': 0,
                                'message': "Both username and password required",
                                'error_code': 400
                            }

                    elif data['type'] == 'signup':
                        if data['username'] and data['password']:
                            data['username'] = str(data['username'])
                            data['password'] = str(data['password'])
                            cur = db_conn.cursor()
                            cur.execute("SELECT id FROM users WHERE username = (%s)", (data['username'], ))
                            res = cur.fetchone()
                            cur.close()

                            if res:
                                reply = {
                                    'status': 0,
                                    'message': "Username already exists",
                                    'error_code': 402
                                }
                            else:
                                passhash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
                                cur = db_conn.cursor()
                                cur.execute(
                                    """
                                    INSERT INTO users(username, password)
                                    VALUES (%s, %s);
                                    """,
                                    (data['username'], passhash)
                                )
                                db_conn.commit()
                                cur.close()
                                token = str(1000 + len(self.connected_players))
                                self.connected_players[data['username']] = {
                                    'username': data['username'],
                                    'token': token,
                                    'ip': addr[0],
                                    'in_room': False
                                }

                                reply = {
                                    'status': 1,
                                    'token': token
                                }
                        else:
                            reply = {
                                'status': 0,
                                'message': "Both username and password are required",
                                'error_code': 400
                            }

                    elif data['type'] == 'logout':
                        if data['username'] and data['token'] and self.connected_players[data['username']]:
                            if self.connected_players[data['username']]['token'] == data['token']:
                                del self.connected_players[data['username']]
                                reply = {
                                    'status': 1
                                }
                            else:
                                reply = {
                                    'status': 0,
                                    'message': "Unauthorized request",
                                    'error_code': 404
                                }
                        else:
                            reply = {
                                'status': 0,
                                'message': "Malformed request",
                                'error_code': 405
                            }

                    elif data['type'] == 'create_room':
                        if data['username'] and data['token'] and self.connected_players[data['username']]:
                            if self.connected_players[data['username']]['token'] == data['token']:
                                room_id = self.available_rooms.pop()
                                self.threaded_create_room(addr, room_id, data['username'], data['token'])

                                reply = {
                                    'status': 1,
                                    'room_id': room_id['room_id'],
                                    'udp_port': self.port + int(room_id['room_no']),
                                    'tcp_port': self.port + int(room_id['room_no']) + 1
                                }
                            else:
                                reply = {
                                    'status': 0,
                                    'message': "Unauthorized request",
                                    'error_code': 404
                                }
                        else:
                            reply = {
                                'status': 0,
                                'message': "Invalid request",
                                'error_code': 405
                            }

                    elif data['type'] == 'join_room':
                        if data['username'] and data['token'] and data['room_id'] and self.connected_players[data['username']]:
                            if self.connected_players[data['username']]['token'] == data['token']:
                                room_no = None
                                for k,v in self.active_rooms.items():
                                    if v['data']['room_id'] == data['room_id']:
                                        room_no = k
                                if room_no:
                                    self.connected_players[data['username']]['in_room'] = {'room_id': data['room_id'], 'room_no': room_no}
                                    self.active_rooms[room_no]['data']['room_info']['players'][data['username']] = {
                                        'ip': addr[0],
                                        'username': data['username'],
                                        'token': data['token'],
                                        'player_object': None,
                                        'player_sprite': None,
                                        'player_no': len(self.active_rooms[room_no]['data']['room_info']['players']),
                                        'ready': False,
                                        'player_loaded': False
                                    }
                                    self.active_rooms[room_no]['data']['room_object'].update_room(self.active_rooms[room_no]['data']['room_info'])

                                    print("Joined room")
                                    print(self.active_rooms)
                                    print(self.connected_players)

                                    reply = {
                                        'status': 1,
                                        'udp_port': self.port + int(room_no),
                                        'tcp_port': self.port + int(room_no) + 1
                                    }

                                else:
                                    reply = {
                                        'status': 0,
                                        'message': "Invalid room id",
                                        'error_code': 300
                                    }
                            else:
                                reply = {
                                    'status': 0,
                                    'message': "Unauthorized request",
                                    'error_code': 404
                                }
                        else:
                            reply = {
                                'status': 0,
                                'message': "Invalid request",
                                'error_code': 405
                            }


                    elif data['type'] == 'exit_room_lobby':
                        if data['username'] and data['token'] and self.connected_players[data['username']]:
                            if self.connected_players[data['username']]['token'] == data['token']:
                                room_no = self.connected_players[data['username']]['in_room']['room_no']
                                if self.active_rooms[room_no]['data']['room_object'].room_close:
                                    del self.active_rooms[room_no]
                                    self.available_rooms.append(self.connected_players[data['username']]['in_room'])
                                self.connected_players[data['username']]['in_room'] = False
                                print("ACTIVE ROOMS ROOM INFO:", self.active_rooms)
                                print("CONNECTED PLAYERS INFO:", self.connected_players)

                                reply = {
                                    'status': 1,
                                }

                            else:
                                reply = {
                                    'status': 0,
                                    'message': "Unauthorized request",
                                    'error_code': 404
                                }
                        else:
                            reply = {
                                'status': 0,
                                'message': "Invalid request",
                                'error_code': 405
                            }

                    elif data['type'] == 'close_game':
                        self.pool.putconn(db_conn)
                        if data['username'] and data['token'] and self.connected_players[data['username']]:
                            if self.connected_players[data['username']]['token'] == data['token'] and self.connected_players[data['username']]['in_room']:
                                if self.active_rooms[room_no]['data']['room_object'].room_close:
                                    del self.active_rooms[room_no]
                                    self.available_rooms.append(self.connected_players[data['username']]['in_room'])
                        reply = {
                            'status': 1
                        }
                    else:
                        reply = {
                            'status': 0,
                            'message': "Invalid request",
                            'error_code': 500
                        }

                    print("Server recieved from:", addr, data)
                    print("Server sending:", reply, "\n\n")

                connection.sendall(pickle.dumps(reply))

                if data['type'] == 'close_game':
                    return

            except KeyError:
                reply = {
                    'status': 0,
                    'message': "Malformed request",
                    'error_code': 405
                }
                connection.sendall(pickle.dumps(reply))

            except socket.error as e:
                print("Socket error:", e)
                return

            except Exception as e:
                print(e)
                reply = {
                    'status': 0,
                    'message': "Server error",
                    'error_code': 501
                }
                connection.sendall(pickle.dumps(reply))

    def run(self):
        while True:
            print(threading.enumerate())
            connection, addr = self.server.accept()
            print("Connected to:", addr)
            db_conn = self.pool.getconn()
            server_thread = threading.Thread(target=self.threaded_client, args=(addr, connection, db_conn))
            server_thread.start()

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 7000

    load_dotenv()
    pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=os.getenv('HOST'),
        dbname=os.getenv('DBNAME'),
        port=os.getenv('PORT'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD')
    )
    server = Server(ip, port, pool)
    server.run()
