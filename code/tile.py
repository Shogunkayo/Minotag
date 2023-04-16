import pygame
from util import import_folder

class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

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
        super().__init__(size, x, y, pygame.image.load(path).convert_alpha())
        # offset as tile size and crate size are different
        offset_y = y + size
        self.rect = self.image.get_rect(bottomleft=(x, offset_y))

class Timer(StaticTile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y, pygame.image.load(path).convert_alpha())
        self.font = pygame.font.Font(None, 64)
        self.colour = (230, 226, 204)
        self.bg_image = self.image.copy()
        self.bg_rect = self.image.get_rect()

    def update(self, time):
        self.image = self.bg_image.copy()
        text_surface = self.font.render(str(time), True, self.colour)
        text_rect = text_surface.get_rect(center=self.bg_rect.center)
        self.image.blit(text_surface, text_rect)

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
