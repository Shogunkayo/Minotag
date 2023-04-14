import pygame
import sys
from game_data import screen_width, screen_height
from network import Network
from time import sleep
import threading

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()

        self.net = Network()
        self.status = 'open'
        self.room_leader = False
        self.current_map = None
        self.player2 = None

        self.connect_server()

    def connect_server(self):
        username = input("Enter username: ")
        req = self.net.send_server({'type': 'login', 'username': username})
        if req['status'] == 1:
            self.status = 'logged_in'
            self.username = username

    def create_room(self):
        req = self.net.send_server({'type': 'create_room'})
        if req['status'] == 1:
            self.status = 'in_room'
            self.room_leader = True
            print(req['tcp_port'])
            print(req['udp_port'])
            sleep(1)
            self.net.connect_tcp(req['tcp_port'])
            self.net.udp_port = req['udp_port']
            self.get_maps()

    def join_room(self):
        room_id = input("Enter room number: ")
        req = self.net.send_server({'type': 'join_room', 'room_id': room_id})
        if req['status'] == 1:
            self.status = 'in_room'
            self.net.connect_tcp(req['tcp_port'])
            self.net.udp_port = req['udp_port']
            self.get_maps()

    def get_maps(self):
        maps = self.net.send_tcp({'type': 'get_maps'})
        self.map_list = maps

    def get_current_map(self):
        if self.room_leader:
            self.current_map_no = int(input("Select map: "))
            self.current_map_no = 0
            self.net.send_tcp({'type': 'set_current_map', 'map_no': self.current_map_no})
        else:
            req = self.net.send_tcp({'type': 'get_current_map'})
            if req['status'] == 0:
                return
            self.current_map_no = req['map']

        self.current_map = self.map_list[self.current_map_no]

    def get_player_1(self):
        req = self.net.send_tcp({'type': 'create_player'})
        if req['status']:
            player = req['player']
            player.import_assets(player.sprite_path)
            player.import_dust_run_assets()

            self.current_map.player_1_setup(player)
            self.status = "loaded_player"
        else:
            print("Error retriveing player")

    def get_player_2(self):
        if not self.player2:
            req = self.net.send_tcp({'type': 'get_player', 'is_leader': self.room_leader})
            if req['status']:
                self.player2 = True
                player = req['players'][0]
                player.import_assets(player.sprite_path)
                player.import_dust_run_assets()
                self.current_map.player_2_setup(player)
                print("Player 2 setup complete")
                self.status = "start_thread"

    def start_thread(self):
        self.current_map.start_thread(self.screen, self.net)
        print("Started client side thread")
        self.status = 'starting_round'

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('gray')

            if self.status == 'open':
                self.connect_server()

            elif self.status == 'logged_in':
                c = int(input("1 => Create Room\n2=> Join Room\n"))
                if c == 1:
                    self.create_room()
                elif c == 2:
                    self.join_room()

            elif self.status == 'in_room':
                self.get_current_map()
                if self.current_map:
                    if self.room_leader:
                        c = int(input("1 => Start Game"))
                        if c == 1:
                            req = self.net.send_tcp({'type': 'start_game', 'is_leader': True})
                            if req['status']:
                                self.status = 'loading_game'
                    else:
                        req = self.net.send_tcp({'type': 'start_game', 'is_leader': False})
                        if req['status']:
                            self.status = 'loading_game'
                        else:
                            sleep(0.5)
                else:
                    sleep(0.5)

            elif self.status == 'loading_game':
                self.current_map.load_sprites()
                self.get_player_1()

            elif self.status == 'loaded_player':
                self.get_player_2()

            elif self.status == 'start_thread':
                self.start_thread()

            elif self.status == 'starting_round':
                self.current_map.run(self.screen)

            else:
                sys.exit()

            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
