import pygame
import sys
from tile import Sprite, TextSprite
from game_data import button_pos, map_thumbnails, sound, error
from string import ascii_letters, digits
from time import time
import socket
import threading

class Button:
    def __init__(self, path, pos, sound=None):
        self.image = pygame.image.load('../assets/ui/buttons/' + path).convert_alpha()
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
    def __init__(self, pos, path='text_input.png', active_colour=(51, 50, 61), font_style='Arcadepix', font_size=32, text_offset_x=0, text_offset_y=0,
                 placeholder='', placeholder_colour=pygame.Color('gray'), maxlen=15, password=False, alnum=True, sound=None):

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
    def __init__(self, pos, max_width, max_height, font_style='Arcadepix', font_colour=(51, 50, 61), font_size=25, text_offset_x=40, text_offset_y=0, padding=0):
        self.image = pygame.image.load('../assets/ui/elements/chat_box.png').convert_alpha()
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

class Home:
    def __init__(self, display_surface, status, net):
        self.display_surface = display_surface
        self.home_sprite = pygame.sprite.Group()
        self.load_assets()
        self.status = status
        self.error_status = None
        self.net = net
        self.room_leader = False
        self.username = None
        self.token = None

    def load_assets(self):
        bg = pygame.image.load('../assets/ui/menus/home.png').convert()
        bg_sprite = Sprite(0, 0, bg)
        self.home_sprite.add(bg_sprite)

        self.login = Button('login.png', button_pos['home_default_top'], sound=sound['click'])
        self.signup = Button('signup.png', button_pos['home_default_bot'], sound=sound['click'])
        self.create = Button('create.png', button_pos['home_default_top'], sound=sound['click'])
        self.join = Button('join.png', button_pos['home_default_bot'], sound=sound['click'])
        self.back = Button('back.png', button_pos['back_btn'], sound=sound['back'])
        self.logout = Button('logout.png', button_pos['logout_btn'], sound=sound['back'])
        self.close = Button('close.png', button_pos['close_btn'], sound=sound['back'])

        self.login_username = TextInput(button_pos['home_input_top'], placeholder='Username', text_offset_x=18, text_offset_y=25, sound=sound['type'])
        self.login_password = TextInput(button_pos['home_input_mid'], placeholder='Password', password=True, text_offset_x=18, text_offset_y=25, sound=sound['type'])
        self.signup_username = TextInput(button_pos['home_input_top'], placeholder='Username', text_offset_x=18, text_offset_y=25, sound=sound['type'])
        self.signup_password = TextInput(button_pos['home_input_mid'], placeholder='Password', password=True, text_offset_x=18, text_offset_y=25, sound=sound['type'])
        self.join_id = TextInput(button_pos['home_default_inp'], placeholder='Room ID', maxlen=5, text_offset_x=18, text_offset_y=25, sound=sound['type'])

        self.error_ui = ErrorUI(error['error_path'], error['error_pos']['home_start'], animation='move', sound=sound['error'])

    def go_login(self):
        self.error_status = None
        self.status = 'login'

    def go_signup(self):
        self.error_status = None
        self.status = 'signup'

    def run_login(self):
        self.error_status = None
        self.username = self.login_username.text_input
        password = self.login_password.text_input
        self.login_password.text_input = ''

        if self.username and password:
            req = self.net.send_server({
                'type': 'login',
                'username': self.username,
                'password': password
            })

            if req['status']:
                self.token = req['token']
                self.status = 'choose_room'
            else:
                self.error_status = req['error_code']
                self.error_ui.set_error(error['error_code'][self.error_status], offset_x=33, offset_y=95)
        else:
            self.error_status = 400
            self.error_ui.set_error(error['error_code'][self.error_status], offset_x=33, offset_y=95)

    def run_signup(self):
        self.error_status = None
        self.username = self.signup_username.text_input
        password = self.signup_password.text_input

        if self.username and password:
            req = self.net.send_server({
                'type': 'signup',
                'username': self.username,
                'password': password
            })

            if req['status']:
                self.token = req['token']
                self.status = 'choose_room'
            else:
                self.error_status = req['error_code']
                self.error_ui.set_error(error['error_code'][self.error_status], offset_x=33, offset_y=95)
        else:
            self.error_status = 400
            self.error_ui.set_error(error['error_code'][self.error_status], offset_x=33, offset_y=95)

    def create_room(self):
        self.error_status = None
        req = self.net.send_server({
            'type': 'create_room',
            'username': self.username,
            'token': self.token
        })

        if req['status']:
            self.status = 'lobby'
            self.room_leader = True
            self.room_id = req['room_id']
            self.tcp_port = req['tcp_port']
            self.udp_port = req['udp_port']
        else:
            self.error_status = req['error_code']
            self.error_ui.set_error(error['error_code'][self.error_status], offset_x=33, offset_y=95)

    def go_join(self):
        self.error_status = None
        self.status = 'join_room'

    def join_room(self):
        self.error_status = None
        self.room_id = str(self.join_id.text_input)

        if self.room_id:
            req = self.net.send_server({
                'type': 'join_room',
                'room_id': self.room_id,
                'username': self.username,
                'token': self.token
            })

            if req['status']:
                self.status = 'lobby'
                self.tcp_port = req['tcp_port']
                self.udp_port = req['udp_port']
            else:
                self.error_status = req['error_code']
                self.error_ui.set_error(error['error_code'][self.error_status], offset_x=33, offset_y=95)
        else:
            self.error_status = 301
            self.error_ui.set_error(error['error_code'][self.error_status], offset_x=33, offset_y=95)

    def back_home(self):
        self.error_status = None
        self.status = 'opened'

    def back_choose(self):
        self.error_status = None
        self.status = 'choose_room'

    def run_logout(self):
        self.error_status = None
        req = self.net.send_server({
            'type': 'logout',
            'username': self.username,
            'token': self.token
        })

        if req['status']:
            self.username = ''
            self.token = ''
            self.status = 'opened'
        else:
            self.error_status = req['error_code']
            self.error_ui.set_error(error['error_code'][self.error_status], offset_x=33, offset_y=95)

    def run_close(self):
        self.net.send_server({
            'type': 'close_game',
            'username': self.username,
            'token': self.token
        }, timeout=3)

        sys.exit()

    def run(self, jump_to_status=None):
        self.home_sprite.draw(self.display_surface)

        if jump_to_status:
            self.status = jump_to_status
            self.room_leader = False

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
            self.back.run(self.display_surface, self.back_home)

        elif self.status == 'signup':
            self.signup.change_pos(button_pos['home_input_bot'])
            self.signup.run(self.display_surface, self.run_signup)
            self.signup_username.draw(self.display_surface)
            self.signup_password.draw(self.display_surface)
            self.back.run(self.display_surface, self.back_home)

        elif self.status == 'choose_room':
            self.create.run(self.display_surface, self.create_room)
            self.join.run(self.display_surface, self.go_join)
            self.logout.run(self.display_surface, self.run_logout)

        elif self.status == 'join_room':
            self.join.run(self.display_surface, self.join_room)
            self.join_id.draw(self.display_surface)
            self.logout.run(self.display_surface, self.run_logout)
            self.back.run(self.display_surface, self.back_choose)

        if self.error_status:
            self.error_ui.run(self.display_surface, error['error_pos']['home_end'])

        self.close.run(self.display_surface, self.run_close)

    def handle_input(self, event):
        if self.status == 'login':
            self.login_username.run(event)
            self.login_password.run(event)

        elif self.status == 'signup':
            self.signup_username.run(event)
            self.signup_password.run(event)

        elif self.status == 'join_room':
            self.join_id.run(event)

class Lobby(threading.Thread):
    def __init__(self, display_surface, net, room_leader, username, token, room_id, map_list):
        threading.Thread.__init__(self)
        self.display_surface = display_surface
        self.net = net
        self.status = 'lobby'
        self.lobby_sprite = pygame.sprite.Group()
        self.room_leader = room_leader
        self.ready = room_leader
        self.username = username
        self.token = token
        self.ready_all = False
        self.map_list = map_list
        self.current_map_no = 0
        self.request_cooldown = 3
        self.last_request_time = 0
        self.thumbnail_pos = map_thumbnails['pos']

        self.load_assets(room_id)

    def load_assets(self, room_id):
        bg = pygame.image.load('../assets/ui/menus/lobby.png').convert()
        bg_sprite = Sprite(0, 0, bg)
        self.lobby_sprite.add(bg_sprite)

        self.left_arrow_btn = Button('left_arrow.png', button_pos['lobby_left_arrow'], sound=sound['type'])
        self.right_arrow_btn = Button('right_arrow.png', button_pos['lobby_right_arrow'], sound=sound['type'])
        self.start_active_btn = Button('start.png', button_pos['lobby_default_top'], sound=sound['click'])
        self.start_inactive_btn = Button('start_inactive.png', button_pos['lobby_default_top'])
        self.ready_btn = Button('ready.png', button_pos['lobby_default_top'], sound=sound['click'])
        self.unready_btn = Button('unready.png', button_pos['lobby_default_top'], sound=sound['back'])
        self.exit_btn = Button('exit.png', button_pos['lobby_default_bot'], sound=sound['back'])

        self.room_id = Text("#" + room_id, button_pos['lobby_room_id'])

        map_thumbnail = pygame.image.load(map_thumbnails['path'][self.current_map_no]).convert_alpha()
        self.map_sprite = pygame.sprite.GroupSingle(Sprite(self.thumbnail_pos[0], self.thumbnail_pos[1], map_thumbnail))

        self.chat_btn = Button('send_chat.png', button_pos['lobby_send_chat'])
        self.chat_input = TextInput(button_pos['lobby_chat_input'], path='chat_input.png', text_offset_x=20, text_offset_y=20, font_size=26, alnum=False, maxlen=50, sound=sound['type'])
        self.chat_display = ChatWindow(button_pos['lobby_chat_display'], 500, 230, text_offset_y=40)
        self.scroll_up_btn = Button('left_arrow.png', (100, 100), sound=sound['type'])
        self.scroll_down_btn = Button('right_arrow.png', (300, 300), sound=sound['type'])

        self.player_sprites = []

    def start_chat_thread(self):
        self.chat_thread = threading.Thread(target=self.threaded_chat)
        self.chat_thread.start()

    def threaded_chat(self):
        while self.status != 'home':
            try:
                message = self.net.get_chat(timeout=10)
                if message is not None:
                    print(message)
                    self.chat_display.update(message['username'] + ': ' + message['message'])
            except socket.timeout:
                pass

    def test(self):
        print("Hehehehaw")

    def get_ready(self):
        current_time = time()
        if current_time - self.last_request_time > self.request_cooldown:
            try:
                req = self.net.send_tcp({
                    'type': 'get_ready',
                    'username': self.username,
                    'token': self.token,
                    'current_map_no': self.current_map_no
                })
            except BrokenPipeError:
                pass

            try:
                if req['status']:
                    self.current_map_no = req['current_map_no']
                    if self.username == req['room_leader']:
                        self.room_leader = True
                    if not self.room_leader:
                        map_thumbnail = pygame.image.load(map_thumbnails['path'][self.current_map_no]).convert_alpha()
                        self.map_sprite = pygame.sprite.GroupSingle(Sprite(self.thumbnail_pos[0], self.thumbnail_pos[1], map_thumbnail))

                    players = req['players']
                    self.ready_all = True
                    i = 0
                    self.player_sprites = []
                    for username, player in players.items():
                        if i == 0:
                            x, y = 122, 521
                        elif i == 1:
                            x, y = 333, 521
                        elif i == 2:
                            x, y = 122, 760
                        else:
                            x, y = 333, 760

                        if len(username) < 7:
                            x_offset = 30/len(username)
                        else:
                            x_offset = - 30/len(username)

                        if not player['ready']:
                            self.ready_all = False
                            self.player_sprites.append({
                                'username': Text(username, (x + x_offset, y-32), font_size=30),
                                'sprite': pygame.sprite.GroupSingle(Sprite(x, y, pygame.image.load(player['player_sprite']+'unready.png').convert_alpha()))
                            })
                        else:
                            self.player_sprites.append({
                                'username': Text(username, (x + x_offset, y-32), font_size=30),
                                'sprite': pygame.sprite.GroupSingle(Sprite(x, y, pygame.image.load(player['player_sprite']+'ready.png').convert_alpha()))
                            })
                        i += 1

                    if req['game_started']:
                        self.status = 'game'

            except TypeError:
                pass

            self.last_request_time = current_time

    def send_chat(self):
        message = self.chat_input.text_input
        if message:
            req = self.net.send_tcp({
                'type': 'chat',
                'username': self.username,
                'token': self.token,
                'message': message
            })
            if req['status']:
                self.chat_input.text_input = ''
            else:
                print("Error occured")

    def run_start(self):
        req = self.net.send_tcp({
            'type': 'start_game',
            'username': self.username,
            'token': self.token,
            'map_no': self.current_map_no
        })

        if req['status']:
            self.status = 'game'

    def run_ready(self):
        req = self.net.send_tcp({
            'type': 'ready',
            'username': self.username,
            'token': self.token
        })

        if req['status']:
            self.ready = True

    def run_unready(self):
        req = self.net.send_tcp({
            'type': 'unready',
            'username': self.username,
            'token': self.token
        })

        if req['status']:
            self.ready = False

    def map_left(self):
        self.current_map_no = (self.current_map_no-1) % len(self.map_list)
        map_thumbnail = pygame.image.load(map_thumbnails['path'][self.current_map_no]).convert_alpha()
        self.map_sprite = pygame.sprite.GroupSingle(Sprite(self.thumbnail_pos[0], self.thumbnail_pos[1], map_thumbnail))

    def map_right(self):
        self.current_map_no = (self.current_map_no+1) % len(self.map_list)
        map_thumbnail = pygame.image.load(map_thumbnails['path'][self.current_map_no]).convert_alpha()
        self.map_sprite = pygame.sprite.GroupSingle(Sprite(self.thumbnail_pos[0], self.thumbnail_pos[1], map_thumbnail))

    def exit_room(self):
        self.net.send_tcp({
            'type': 'exit_room_lobby',
            'username': self.username,
            'token': self.token
        })
        self.net.send_server({
            'type': 'exit_room_lobby',
            'username': self.username,
            'token': self.token
        })
        self.net.close_tcp()
        self.net.close_chat()
        self.net.send_udp({
            'type': 'exit_room_lobby',
            'username': self.username,
            'token': self.token,
        })

        self.net.close_udp()
        self.status = 'home'

    def run(self, jump_to_status=None):

        if jump_to_status:
            self.status = 'lobby'
            self.ready = False

        self.lobby_sprite.draw(self.display_surface)
        self.room_id.draw(self.display_surface)
        self.map_sprite.draw(self.display_surface)
        self.chat_display.run(self.display_surface)
        self.chat_input.draw(self.display_surface)
        self.chat_btn.run(self.display_surface, self.send_chat)
        self.get_ready()

        if self.room_leader:
            self.left_arrow_btn.run(self.display_surface, self.map_left)
            self.right_arrow_btn.run(self.display_surface, self.map_right)
            if self.ready_all:
                self.start_active_btn.run(self.display_surface, self.run_start)
            else:
                self.start_inactive_btn.run(self.display_surface, self.test)
        else:
            if self.ready:
                self.unready_btn.run(self.display_surface, self.run_unready)
            else:
                self.ready_btn.run(self.display_surface, self.run_ready)

        for player_sprite in self.player_sprites:
            player_sprite['sprite'].draw(self.display_surface)
            player_sprite['username'].draw(self.display_surface)

        self.exit_btn.run(self.display_surface, self.exit_room)

        self.scroll_up_btn.run(self.display_surface, self.chat_display.decrement_line)
        self.scroll_down_btn.run(self.display_surface, self.chat_display.increment_line)

    def handle_input(self, event):
        self.chat_input.run(event)

class Endscreen:
    def __init__(self, display_surface, loser):
        self.display_surface = display_surface
        self.end_sprite = pygame.sprite.Group()
        self.load_assets(loser)
        self.status = 'end'

    def load_assets(self, loser):
        try:
            bg = pygame.image.load('../assets/end_screen.png').convert()
            bg = pygame.transform.scale(bg, (1920, 1080))
        except:
            bg = pygame.image.load('../assets/ui/elements/bg.png').convet()
        bg_sprite = Sprite(0, 0, bg)
        self.end_sprite.add(bg_sprite)
        fg = pygame.image.load('../assets/ui/menus/end.png').convert_alpha()
        fg_sprite = Sprite(0, 0, fg)
        self.end_sprite.add(fg_sprite)

        if len(loser['username']) < 6:
            x_offset = 30/len(loser['username'])
        else:
            x_offset = - 30/len(loser['username'])
        self.loser_txt = Text(loser['username'], (button_pos['end_default_txt'][0] + x_offset, button_pos['end_default_txt'][1]), font_size=30)
        self.loser_sprite = pygame.sprite.GroupSingle(Sprite(button_pos['end_default_sprite'][0], button_pos['end_default_sprite'][1], pygame.image.load(loser['player_sprite']+'unready.png').convert_alpha()))

        self.lobby_btn = Button('lobby.png', button_pos['end_default_btn'], sound=sound['click'])

    def go_lobby(self):
        self.status = 'lobby'

    def run(self):
        self.end_sprite.draw(self.display_surface)
        self.loser_txt.draw(self.display_surface)
        self.loser_sprite.draw(self.display_surface)
        self.lobby_btn.run(self.display_surface, self.go_lobby)

if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((1920, 1080))
    lobby = Lobby(screen, 'hehe', 'hehaw')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        lobby.run()

        pygame.display.update()
