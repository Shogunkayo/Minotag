import pygame
import sys
from game_data import screen_width, screen_height
from network import Network

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()

        self.net = Network()
        self.status = 'open'

        self.connect_server()
        self.join_room()

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
            self.net.connect_tcp(req['tcp_port'])

    def join_room(self):
        room_id = input("Enter room number: ")
        req = self.net.send_server({'type': 'join_room', 'room_id': room_id})
        if req['status'] == 1:
            self.status = 'in_room'
            self.net.connect_tcp(req['tcp_port'])

    def get_maps(self):
        print("Sent")
        maps = self.net.send({'type': 'map_list'})
        print("Received")
        self.map_list = maps

    def get_current_map(self):
        if self.room_leader:
            self.current_map_no = int(input("Select map: "))
            self.current_map_no = 0
        self.current_map = self.map_list[self.current_map_no]
        self.current_map.load_sprites()

    def get_player_1(self):
        player = self.net.send({'type': 'create_player', 'id': 0})
        print(player)
        player.import_assets(player.sprite_path)
        print(player.sprite_path)
        player.import_dust_run_assets()

        self.current_map.player_1_setup(player)

    def get_player_2(self):
        if not self.player2:
            player = self.net.send({'type': 'get_player'})
            if player:
                self.player2 = True
                player.import_assets(player.sprite_path)
                player.import_dust_run_assets()
                self.current_map.player_2_setup(player)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('gray')
            self.get_player_2()
            self.current_map.run(self.screen, self.net)
            pygame.display.update()
            self.clock.tick(120)

if __name__ == "__main__":
    game = Game()
