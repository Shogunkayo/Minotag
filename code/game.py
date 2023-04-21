import pygame
import sys
from game_data import screen_width, screen_height
from network import Network
from time import sleep
import signal
from ui import Home, Lobby

class Game:
    '''
    Game object which the client uses
    '''

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()

        self.net = Network()
        self.status = 'home'
        self.current_map = None
        self.player2 = None
        self.home = Home(self.screen, 'opened', self.net)
        self.lobby = None

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
        print("PLAYER INIT CALLED", )
        if req['status']:
            self.map_list = req['map_list']
            self.player_sprite = req['player_sprite']
        else:
            print("Error initializing player")
            self.status = 'home'

    def get_player_1(self):
        req = self.net.send_tcp({'type': 'create_player'})

        if req['status']:
            player = req['player']
            player.import_assets(player.sprite_path)
            player.import_dust_run_assets()
            self.current_map.player_1_setup(player, self.username)
            self.status = "loaded_player"
        else:
            print("Error retriveing player")

    def get_player_2(self):
        if not self.player2:
            req = self.net.send_tcp({'type': 'get_player', 'is_leader': self.room_leader})

            if req['status']:
                self.player2 = True
                player = req['players'][0]
                player.import_assets(player.sprite_path)
                player.import_dust_run_assets()
                self.current_map.player_2_setup(player)
                print("Player 2 setup complete")
                self.status = "start_thread"

    def start_thread(self):
        print("Started client side thread")
        self.status = 'starting_round'

    def game_restart(self):
        if self.room_leader:
            c = int(input("1 => Restart\n"))

            if c == 1:
                req = self.net.send_tcp({'type': 'do_restart', 'is_leader': self.room_leader})

                if req['status']:
                    self.current_map.game_reset(self.net)
        else:
            print("Waiting for room leader to restart")
            req = self.net.send_tcp({'type': 'is_restart'})
            try:
                if req['status']:
                    self.current_map.game_reset(self.net)
                else:
                    sleep(0.5)
            except TypeError:
                pass

    def stop_threads(self, sig, frame):
        try:
            self.net.send_tcp({'type': 'kill'}, timeout=1)
            self.net.send_udp({'type': 'kill'}, timeout=1)
        except:
            pass

        self.net.send_server({'type': 'kill'}, timeout=1)
        sys.exit()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.stop_threads()
                    pygame.quit()
                    sys.exit()
                if self.status == 'home':
                    self.home.handle_input(event)

            self.screen.fill('gray')

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
                        self.lobby.run('lobby')

            elif self.status == 'lobby':
                self.lobby.run('lobby')
                if self.lobby.status == 'game':
                    self.status = 'game'
                elif self.lobby.status == 'home':
                    self.status = 'home'
                    self.room_id = None
                    self.room_leader = False
                    self.home.run('choose_room')

                self.room_leader = self.lobby.room_leader

            elif self.status == 'loading_game':
                self.current_map.load_sprites()
                self.get_player_1()

            elif self.status == 'loaded_player':
                self.get_player_2()

            elif self.status == 'start_thread':
                self.start_thread()

            elif self.status == 'starting_round':
                self.current_map.run(self.screen, self.net)
                if self.current_map.game_ended:
                    self.game_restart()
                    if self.current_map.p1_is_leader:
                        self.room_leader = True

            else:
                sys.exit()

            signal.signal(signal.SIGINT, self.stop_threads)

            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
