import pygame
from game_data import tile_size, vertical_tile_number, screen_width, map_sprites
from pygame_util import import_folder, StaticTile
from random import choice, randint

class Sky:
    def __init__(self, horizon):
        self.top = pygame.image.load(map_sprites['sky_top'])
        self.middle = pygame.image.load(map_sprites['sky_middle'])
        self.bottom = pygame.image.load(map_sprites['sky_bottom'])
        self.horizon = horizon

        self.top = pygame.transform.scale(self.top, (screen_width, tile_size))
        self.middle = pygame.transform.scale(self.middle, (screen_width, tile_size))
        self.bottom = pygame.transform.scale(self.bottom, (screen_width, tile_size))

    def draw(self, surface):
        for row in range(vertical_tile_number):
            x = 0
            y = row * tile_size

            if row < self.horizon:
                surface.blit(self.top, (x, y))
            elif row == self.horizon:
                surface.blit(self.middle, (x,y))
            else:
                surface.blit(self.bottom, (x,y))

class Clouds:
    def __init__(self, horizon, level_width, cloud_number):
        cloud_surf_list = import_folder(map_sprites['clouds'])
        min_x = -screen_width
        max_x = level_width + screen_width
        min_y = 0
        max_y = horizon
        self.cloud_sprites = pygame.sprite.Group()

        for cloud in range(cloud_number):
            cloud = choice(cloud_surf_list)
            x = randint(min_x, max_x)
            y = randint(min_y, max_y)
            sprite = StaticTile(0, x, y, cloud)
            self.cloud_sprites.add(sprite)

    def draw(self, surface, shift):
        self.cloud_sprites.update(shift, 0)
        self.cloud_sprites.draw(surface)
