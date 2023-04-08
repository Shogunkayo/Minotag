import pygame
import sys
from settings import screen_width, screen_height
from network import Network

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()

        self.net = Network()

        self.get_maps()
        self.get_current_map()
        self.get_players()

    def get_maps(self):
        maps = self.net.send({'type': 'map_list'})
        self.map_list = maps

    def get_current_map(self):
        self.current_map = 0
        self.map_list[self.current_map].load_sprites()

    def get_players(self):
        self.id = self.net.send({'type': 'get_id'})
        print(self.id)
        player = self.net.send({'type': 'create_player', 'id': self.id})
        print(player)
        player[0].import_assets()
        player[0].import_dust_run_assets()
        self.map_list[self.current_map].player_setup(player[0])

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('gray')

            self.map_list[self.current_map].run(self.screen)

            pygame.display.update()
            self.clock.tick(120)

if __name__ == "__main__":
    game = Game()
    game.run()
