import pygame
import sys
from game_data import screen_width, screen_height, music
from network import Network
from time import sleep
import signal
from ui import Home, Lobby, Endscreen

class Game:
    '''
    Game object which the client uses
    '''

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption("Minotag")
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        pygame.mixer.music.load(music['lobby'])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.net = Network()
        self.status = 'home'
        self.current_map = None
        self.player2 = None
        self.home = Home(self.screen, 'opened', self.net)
        self.lobby = None
        self.loaded_sprites = False

    def display_room(self):
        if self.current_map:
            if self.room_leader:
                c = int(input("1 => Start Game\n"))
                if c == 1:
                    req = self.net.send_tcp({'type': 'start_game', 'is_leader': True})
                    if req['status']:
                        self.status = 'loading_game'
            else:
                req = self.net.send_tcp({'type': 'start_game', 'is_leader': False})
                if req['status']:
                    self.status = 'loading_game'
                else:
                    sleep(0.5)
        else:
            sleep(0.5)

    def player_init(self):
        req = self.net.send_tcp({
            'type': 'player_init',
            'username': self.username,
            'token': self.token
        })
        if req['status']:
            self.map_list = req['map_list']
            self.player_sprite = req['player_sprite']
        else:
            print("Error initializing player")
            self.status = 'home'

    def load_player(self):
        req = self.net.send_tcp({
            'type': 'create_player',
            'username': self.username,
            'token': self.token
        })

        if req['status']:
            player = req['player_object']
            player.import_assets()
            player.import_dust_run_assets()
            self.current_map.player_setup(player, self.username)

            req = self.net.send_tcp({
                'type': 'player_loaded',
                'username': self.username,
                'token': self.token
            })

            if req['status']:
                self.loaded_sprites = True

    def check_start(self):
        req = self.net.send_tcp({
            'type': 'check_start',
            'username': self.username,
            'token': self.token
        })

        if req['status']:
            req = self.net.send_tcp({
                'type': 'load_others',
                'username': self.username,
                'token': self.token,
            })

            if req['status']:
                self.current_map.load_others(req['other_players'])
                self.status = 'play'

    def game_ended(self):
        req = self.net.send_tcp({
            'type': 'game_ended',
            'username': self.username,
            'token': self.token
        })

        if req['status']:
            self.loser = req

    def stop_threads(self, sig=None, frame=None):
        try:
            self.net.send_tcp({'type': 'close_game'}, timeout=1)
        except:
            pass
        try:
            self.net.send_udp({'type': 'close_game'}, timeout=1)
        except:
            pass
        try:
            self.net.send_server({'type': 'close_game'}, timeout=1)
        except:
            pass
        sys.exit()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_threads()
                    pygame.quit()
                    sys.exit()
                if self.status == 'home':
                    self.home.handle_input(event)
                if self.status == 'lobby':
                    self.lobby.handle_input(event)

            self.screen.fill((51, 50, 61))

            if self.status == 'home':
                self.home.run()
                if self.home.status == 'lobby':
                    self.status = 'lobby'
                    self.username = self.home.username
                    self.token = self.home.token
                    self.room_leader = self.home.room_leader
                    self.room_id = self.home.room_id
                    sleep(3)
                    self.net.connect_tcp(self.home.tcp_port)
                    self.net.udp_port = self.home.udp_port
                    self.player_init()
                    if self.status == 'lobby':
                        self.lobby = Lobby(self.screen, self.net, self.room_leader, self.username, self.token, self.room_id, self.map_list)
                        self.lobby.start_chat_thread()
                        self.lobby.run('lobby')

            elif self.status == 'lobby':
                self.lobby.run()
                if self.lobby.status == 'game':
                    self.status = 'game'
                    pygame.mixer.music.fadeout(1000)
                    pygame.mixer.music.unload()
                    pygame.mixer.music.load(music['game'])
                    pygame.mixer.music.play(-1)
                    self.current_map_no = self.lobby.current_map_no
                elif self.lobby.status == 'home':
                    self.status = 'home'
                    self.room_id = None
                    self.room_leader = False
                    self.home.run('choose_room')

                self.room_leader = self.lobby.room_leader

            elif self.status == 'game':
                if not self.loaded_sprites:
                    self.current_map = self.map_list[self.current_map_no][1]
                    self.current_map.load_sprites()
                    self.load_player()
                else:
                    self.check_start()

            elif self.status == 'play':
                self.current_map.run(self.screen, self.net, self.token)
                if self.current_map.game_ended:
                    self.status = 'end'
                    pygame.mixer.music.fadeout(1000)
                    pygame.mixer.music.unload()
                    self.game_ended()
                    self.endscreen = Endscreen(self.screen, self.loser)

            elif self.status == 'end':
                self.endscreen.run()
                self.current_map.game_ended = False
                self.loaded_sprites = False
                if self.endscreen.status == 'lobby':
                    pygame.mixer.music.fadeout(1000)
                    pygame.mixer.music.unload()
                    pygame.mixer.music.load(music['lobby'])
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    self.status = 'lobby'
                    self.lobby.run('lobby')

            else:
                sys.exit()

            signal.signal(signal.SIGINT, self.stop_threads)

            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
