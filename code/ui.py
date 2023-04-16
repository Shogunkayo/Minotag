import pygame
import sys
from tile import Sprite
from game_data import button_pos

class Button:
    def __init__(self, path, pos):
        self.image = pygame.image.load('../assets/ui/buttons/' + path).convert_alpha()
        self.button_sprite = pygame.sprite.GroupSingle(Sprite(pos[0], pos[1], self.image))

        self.pressed = False

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
                    print("Click")
                    callback()
                    self.pressed = False

    def run(self, display_surface, callback):
        self.button_sprite.draw(display_surface)
        self.on_click(callback)

class Home:
    def __init__(self, display_surface, status):
        self.display_surface = display_surface
        self.home_sprite = pygame.sprite.Group()
        self.load_assets()
        self.status = status

    def load_assets(self):
        bg = pygame.image.load('../assets/ui/menus/home.png').convert_alpha()
        bg_sprite = Sprite(0, 0, bg)
        self.home_sprite.add(bg_sprite)

        self.login = Button('login.png', button_pos['home_default_top'])
        self.signup = Button('signup.png', button_pos['home_default_bot'])
        self.create = Button('create.png', button_pos['home_default_top'])
        self.join = Button('join.png', button_pos['home_default_bot'])

    def test1(self):
        self.status = 'in_lobby'

    def test2(self):
        self.status = 'opened'

    def run(self):
        self.home_sprite.draw(self.display_surface)

        if self.status == 'opened':
            self.login.run(self.display_surface, self.test1)
            self.signup.run(self.display_surface, self.test2)

        elif self.status == 'in_lobby':
            self.create.run(self.display_surface, self.test1)
            self.join.run(self.display_surface, self.test2)

if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((1920, 1080))
    home = Home(screen, 'opened')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        home.run()

        pygame.display.update()
