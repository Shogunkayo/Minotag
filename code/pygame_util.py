import pygame
from csv import reader
from os import walk
from game_data import tile_size
from string import ascii_letters, digits

def import_folder(path):
    surface_list = []

    for _, __, images in walk(path):
        for image in images:
            full_path = path + '/' + image
            img_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(img_surface)

    return surface_list

def import_csv_layout(path):
    terrain_map = []

    with open(path) as map:
        level = reader(map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))

    return terrain_map

def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_size()[0] / tile_size)
    tile_num_y = int(surface.get_size()[1] / tile_size)

    cut_tiles = []

    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tile_size
            y = row * tile_size

            new_surface = pygame.Surface((tile_size, tile_size), flags=pygame.SRCALPHA)
            new_surface.blit(surface, (0,0), pygame.Rect(x,y,tile_size, tile_size))
            cut_tiles.append(new_surface)

    return cut_tiles

class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class TextSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, path, font_style='Arcadepix', font_colour=pygame.Color('coral2'), font_size=25, text_offset_x=0, text_offset_y=0):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.bg_image = self.image.copy()
        self.font_colour = font_colour
        self.font_style = font_style
        self.font_size = font_size
        self.font = pygame.font.SysFont(self.font_style, self.font_size)
        self.rect = self.image.get_rect()

    def update(self, text, offset_x, offset_y, font_style=None, font_size=None, font_colour=None):
        self.image = self.bg_image.copy()
        text_surface = self.font.render(text, True, self.font_colour)
        self.image.blit(text_surface, (offset_x, offset_y))

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

class Button:
    def __init__(self, path, pos, sound=None):
        self.image = pygame.image.load(path).convert_alpha()
        self.button_sprite = pygame.sprite.GroupSingle(Sprite(pos[0], pos[1], self.image))

        self.pressed = False
        self.sound = None
        if sound:
            self.sound = pygame.mixer.Sound(sound)

    def change_pos(self, pos):
        self.button_sprite.sprite.rect.x = pos[0]
        self.button_sprite.sprite.rect.y = pos[1]

    def on_click(self, callback):
        mouse_pos = pygame.mouse.get_pos()
        if self.button_sprite.sprite.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
            else:
                if self.pressed:
                    if self.sound:
                        self.sound.play()
                    callback()
                    self.pressed = False

    def run(self, display_surface, callback):
        self.button_sprite.draw(display_surface)
        self.on_click(callback)

class Text:
    def __init__(self, text, pos, colour=pygame.Color('gray94'), font_style='Arcadepix', font_size=70, maxlen=15):
        self.text = text
        self.pos = pos
        self.colour = colour
        self.font = pygame.font.SysFont(font_style, font_size)

    def draw(self, display_surface):
        text_surface = self.font.render(self.text, True, self.colour)
        display_surface.blit(text_surface, self.pos)

class ErrorUI:
    def __init__(self, path, pos, animation=None, sound=None):
        self.pos = pos
        self.error_sprite = pygame.sprite.GroupSingle(TextSprite(pos[0], pos[1], path))
        self.animation = animation
        self.sound = None
        if sound:
            self.sound = pygame.mixer.Sound(sound)

    def set_error(self, text, offset_x=0, offset_y=0, font_style=None, font_size=None, font_colour=None):
        self.error_sprite.sprite.rect.x = self.pos[0]
        self.error_sprite.sprite.rect.y = self.pos[1]
        self.error_sprite.sprite.update(text, offset_x, offset_y, font_style=font_style, font_size=font_size, font_colour=font_colour)
        if self.sound:
            self.sound.play()

    def run(self, display_surface, end_pos=None, animation_speed_x=10, animation_speed_y=10):
        if not end_pos:
            end_pos = self.pos
        if self.animation == 'move':
            if self.error_sprite.sprite.rect.x < end_pos[0]:
                self.error_sprite.sprite.rect.x += animation_speed_x
            elif self.error_sprite.sprite.rect.x > end_pos[0]:
                self.error_sprite.sprite.rect.x -= animation_speed_x
            if self.error_sprite.sprite.rect.y > end_pos[1]:
                self.error_sprite.sprite.rect.y -= animation_speed_y
            elif self.error_sprite.sprite.rect.y < end_pos[1]:
                self.error_sprite.sprite.rect.y += animation_speed_y
        self.error_sprite.draw(display_surface)

class TextInput:
    def __init__(self, path, pos, active_colour=(51, 50, 61), font_style='Arcadepix', font_size=32, text_offset_x=0, text_offset_y=0,
                 placeholder='', placeholder_colour=pygame.Color('gray'), maxlen=15, password=False, alnum=True, sound=None):

        self.image = pygame.image.load(path).convert_alpha()
        self.text_sprite = pygame.sprite.GroupSingle(Sprite(pos[0], pos[1], self.image))
        self.pos = pos
        self.text_input = ''
        self.active_colour = active_colour
        self.placeholder = placeholder
        self.placeholder_colour = placeholder_colour
        self.font = pygame.font.SysFont(font_style, font_size)
        self.maxlen = maxlen
        self.active = False
        self.pressed = 0
        self.password = password
        self.text_offset_x = text_offset_x
        self.text_offset_y = text_offset_y
        self.alnum = alnum
        self.sound = None
        if sound:
            self.sound = pygame.mixer.Sound(sound)

    def on_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.text_sprite.sprite.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.active = True
        else:
            self.active = False

    def draw(self, display_surface):
        self.text_sprite.draw(display_surface)

        if self.text_input == '':
            text = self.placeholder
            colour = self.placeholder_colour
        elif self.password:
            text = '*' * len(self.text_input)
            colour = self.active_colour
        else:
            text = self.text_input
            colour = self.active_colour

        text_surface = self.font.render(text, True, colour)
        display_surface.blit(text_surface, (self.pos[0] + self.text_offset_x, self.pos[1] + self.text_offset_y))

    def run(self, event):
        self.on_click()

        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
            else:
                if len(self.text_input) < self.maxlen:
                    if self.alnum:
                        if event.unicode in ascii_letters + digits:
                            self.text_input += event.unicode
                    else:
                        self.text_input += event.unicode
                    if self.sound:
                        self.sound.play()

class ChatWindow:
    def __init__(self, path, pos, max_width, max_height, font_style='Arcadepix', font_colour=(51, 50, 61), font_size=25, text_offset_x=40, text_offset_y=0, padding=0):
        self.image = pygame.image.load(path).convert_alpha()
        self.image_sprite = pygame.sprite.GroupSingle(Sprite(pos[0], pos[1], self.image))
        self.surface = pygame.Surface((max_width, 1080), pygame.SRCALPHA)
        self.text_window = self.surface.subsurface((0, 0), (max_width, max_height))
        self.font_colour = font_colour
        self.font = pygame.font.SysFont(font_style, font_size)
        self.max_width = max_width
        self.max_height = max_height
        self.text_offset_x = text_offset_x
        self.text_offset_y = text_offset_y
        self.padding = padding
        self.font_size = font_size
        self.cursor = 0
        self.scroll_line = 0

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            if font.render(current_line + word, True, self.font_colour).get_rect().width <= max_width:
                current_line += word + ' '
            else:
                lines.append(current_line.strip())
                current_line = word + ' '

        if current_line:
            lines.append(current_line.strip())

        return lines

    def increment_line(self):
        if self.scroll_line < self.cursor:
            self.scroll_line += self.font_size
            self.update_window()

    def decrement_line(self):
        if self.scroll_line > 0:
            self.scroll_line -= self.font_size
            self.update_window()

    def update(self, text):
        lines = self.wrap_text(text, self.font, self.max_width)
        text_surface = pygame.Surface((self.max_width, self.font_size * len(lines)), pygame.SRCALPHA)
        y = 0
        for line in lines:
            rendered_text = self.font.render(line, True, self.font_colour)
            text_surface.blit(rendered_text, (0, y))
            y += self.font_size

        self.surface.blit(text_surface, (0, self.cursor))
        self.cursor += y

        if self.cursor > self.max_height:
            self.scroll_line += y

        if self.cursor > self.surface.get_rect().height - 200:
            pygame.transform.scale(self.surface, (self.surface.get_rect().width, self.surface.get_rect().height * 2))

        print(self.cursor, self.scroll_line, y)
        self.update_window()

    def update_window(self):
        self.text_window = self.surface.subsurface((0, self.scroll_line), (self.max_width, self.max_height))

    def run(self, display_surface):
        self.image_sprite.draw(display_surface)
        display_surface.blit(self.text_window, (self.image_sprite.sprite.rect.x + self.text_offset_x, self.image_sprite.sprite.rect.y + self.text_offset_y))
