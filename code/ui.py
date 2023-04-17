import pygame
import sys
from tile import Sprite
from game_data import button_pos
from string import ascii_letters, digits

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
                    callback()
                    self.pressed = False

    def run(self, display_surface, callback):
        self.button_sprite.draw(display_surface)
        self.on_click(callback)

class Text:
    def __init__(self, pos, path='text_input.png', active_colour=(51, 50, 61), font_style='Arcadepix', font_size=32, text_offset_x=0, text_offset_y=0,
                 placeholder='', placeholder_colour=pygame.Color('gray'), maxlen=15, password=False, alnum=True):

        self.image = pygame.image.load('../assets/ui/elements/' + path).convert_alpha()
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
                    if self.password:
                        self.text_input += '*'
                    elif self.alnum:
                        if event.unicode in ascii_letters + digits:
                            self.text_input += event.unicode
                    else:
                        self.text_input += event.unicode

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

        self.login_username = Text(button_pos['home_input_top'], placeholder='Username', text_offset_x=18, text_offset_y=25)
        self.login_password = Text(button_pos['home_input_mid'], placeholder='Password', password=True, text_offset_x=18, text_offset_y=25)
        self.signup_username = Text(button_pos['home_input_top'], placeholder='Username', password=True, text_offset_x=18, text_offset_y=25)
        self.signup_password = Text(button_pos['home_input_mid'], placeholder='Password', text_offset_x=18, text_offset_y=25)
        self.join_id = Text(button_pos['home_default_inp'], placeholder='Room ID', maxlen=6, text_offset_x=18, text_offset_y=25)

    def go_login(self):
        self.status = 'login'

    def go_signup(self):
        self.status = 'signup'

    def run_login(self):
        self.status = 'choose_room'

    def run_signup(self):
        self.status = 'choose_room'

    def create_room(self):
        self.status = 'opened'

    def go_join(self):
        self.status = 'join_room'

    def join_room(self):
        self.status = 'opened'

    def run(self):
        self.home_sprite.draw(self.display_surface)

        if self.status == 'opened':
            self.login.change_pos(button_pos['home_default_top'])
            self.signup.change_pos(button_pos['home_default_bot'])
            self.login.run(self.display_surface, self.go_login)
            self.signup.run(self.display_surface, self.go_signup)

        elif self.status == 'login':
            self.login.change_pos(button_pos['home_input_bot'])
            self.login.run(self.display_surface, self.run_login)
            self.login_username.draw(self.display_surface)
            self.login_password.draw(self.display_surface)

        elif self.status == 'signup':
            self.signup.change_pos(button_pos['home_input_bot'])
            self.signup.run(self.display_surface, self.run_signup)
            self.signup_username.draw(self.display_surface)
            self.signup_password.draw(self.display_surface)

        elif self.status == 'choose_room':
            self.create.run(self.display_surface, self.create_room)
            self.join.run(self.display_surface, self.go_join)

        elif self.status == 'join_room':
            self.join.run(self.display_surface, self.join_room)
            self.join_id.draw(self.display_surface)

    def handle_input(self, event):
        if self.status == 'login':
            self.login_username.run(event)
            self.login_password.run(event)

        elif self.status == 'signup':
            self.signup_username.run(event)
            self.signup_password.run(event)

        elif self.status == 'join_room':
            self.join_id.run(event)

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
            home.handle_input(event)

        home.run()

        pygame.display.update()
