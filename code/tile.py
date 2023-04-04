import pygame
from util import import_folder

class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=(x,y))

    def update(self, x_shift, y_shift):
        self.rect.x += x_shift
        self.rect.y += y_shift

# Static tile class for all static tiles that can be added in future
class StaticTile(Tile):
    def __init__(self, size, x, y, surface):
        super().__init__(size, x, y)
        self.image = surface

class Crate(StaticTile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y,
                         pygame.image.load(path).convert_alpha())
        # offset as tile size and crate size are different
        offset_y = y + size
        self.rect = self.image.get_rect(bottomleft=(x, offset_y))

# Animated tile class for all animated tiles that can be added in future
class AnimatedTile(Tile):
    def __init__(self, size, x, y, path):
        super().__init__(size,x,y)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += 0.225
        self.image = self.frames[int(self.frame_index) % len(self.frames) - 1]

    def update(self, x_shift, y_shift):
        self.animate()
        self.rect.x += x_shift
        self.rect.y += y_shift

class Coin(AnimatedTile):
    def __init__(self, size, x, y, path):
        super().__init__(size,x,y,path)
        center_x = x + int(size/2)
        center_y = y + int(size/2)
        self.rect = self.image.get_rect(center=(center_x, center_y))

class Palm(AnimatedTile):
    def __init__(self, size, x, y, path, offset):
        super().__init__(size, x, y, path)
        offset_y = y - offset
        self.rect = self.image.get_rect(topleft=(x, offset_y))
