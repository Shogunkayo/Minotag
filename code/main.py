import pygame
import sys
from settings import screen_width, screen_height
from game import Game
from maps import Map0
from network import Network

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

clientNumber = 0

net = Network()
map0 = Map0(screen, net)
map_list = [map0]
game = Game(0, map_list, screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('gray')
    game.run()

    pygame.display.update()
    clock.tick(60)
