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
        self.player2 = False

        self.get_maps()
        self.get_current_map()
        self.get_player_1()

    def get_maps(self):
        maps = self.net.send({'type': 'map_list'})
        self.map_list = maps

    def get_current_map(self):
        self.current_map = 0
        self.map_list[self.current_map].load_sprites()

    def get_player_1(self):
        player = self.net.send({'type': 'create_player', 'id': 0})
        print(player)
        player.import_assets()
        player.import_dust_run_assets()

        self.map_list[self.current_map].player_1_setup(player)

    def get_player_2(self):
        if not self.player2:
            player = self.net.send({'type': 'get_player'})
            if player:
                self.player2 = True
                player.import_assets()
                player.import_dust_run_assets()
                self.map_list[self.current_map].player_2_setup(player)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('gray')
            self.get_player_2()
            self.map_list[self.current_map].run(self.screen, self.net)
            pygame.display.update()
            self.clock.tick(120)

if __name__ == "__main__":
    game = Game()
    game.run()
