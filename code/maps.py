import pygame
from game_data import tile_size, screen_width, maps, sound, map_sprites
from tile import StaticTile, Coin, Crate, Palm, Timer
from util import import_csv_layout, import_cut_graphics
from decorations import Sky, Clouds

class BaseMap:
    def __init__(self, map):
        self.world_shift_x = 0
        self.other_players = None


        self.last_tag = 0
        self.timer = 10
        self.max_updates = 60
        self.last_update = 0
        self.max_interpolation_delay = 0.1
        self.since_last_update = 0
        self.update = None

        self.game_ended = False
        self.loser = None

        self.thread_started = False

        self.p1_is_leader = False

        self.map = map

    def load_sprites(self):
        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # terrain
        terrain_layout = import_csv_layout(maps[self.map]['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        # grass
        grass_layout = import_csv_layout(maps[self.map]['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        # crates
        crate_layout = import_csv_layout(maps[self.map]['crate'])
        self.crate_sprites = self.create_tile_group(crate_layout, 'crate')

        # power
        power_layout = import_csv_layout(maps[self.map]['power'])
        self.power_sprites = self.create_tile_group(power_layout, 'power')

        # palm fg
        palm_fg_layout = import_csv_layout(maps[self.map]['palm_fg'])
        self.palm_fg_sprites = self.create_tile_group(palm_fg_layout, 'palm_fg')

        # palm bg
        palm_bg_layout = import_csv_layout(maps[self.map]['palm_bg'])
        self.palm_bg_sprites = self.create_tile_group(palm_bg_layout, 'palm_bg')

        # decoration
        self.sky = Sky(10)
        level_width = len(terrain_layout[0]) * tile_size
        self.clouds = Clouds(400, level_width, 20)

        timer_path = map_sprites['timer']
        timer_bg = Timer(256, (screen_width/2) - 84, 10, timer_path)
        self.timer_sprite = pygame.sprite.GroupSingle()
        self.timer_sprite.add(timer_bg)

        self.tag_sound = pygame.mixer.Sound(sound['tag'])

    def player_setup(self, player, username):
        self.player = pygame.sprite.GroupSingle()
        self.player.add(player)
        self.username = username

    def load_others(self, other_players):
        self.other_players = other_players
        for k in self.other_players:
            self.other_players[k]['pos'] = pygame.math.Vector2(0, 0)
            self.other_players[k]['player_object'].import_assets()
            self.other_players[k]['player_object'].import_dust_run_assets()
            self.other_players[k]['sprite'] = pygame.sprite.GroupSingle()
            self.other_players[k]['sprite'].add(self.other_players[k]['player_object'])

    def manage_timer(self, display_surface):
        if self.timer == 0:
            self.game_ended = True
            self.get_screenshot(display_surface)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, col in enumerate(row):
                if col != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics(map_sprites['terrain'])
                        tile_surface = terrain_tile_list[int(col)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'grass':
                        grass_tile_list = import_cut_graphics(map_sprites['grass'])
                        grass_surface = grass_tile_list[int(col)]
                        sprite = StaticTile(tile_size, x, y, grass_surface)

                    if type == 'crate':
                        sprite = Crate(tile_size, x, y, map_sprites['crate'])

                    if type == 'power':
                        if col == '1':
                            sprite = Coin(tile_size, x, y, map_sprites['silver'])

                        if col == '0':
                            sprite = Coin(tile_size, x, y, map_sprites['gold'])

                    if type == 'palm_fg':
                        if col == '5':
                            sprite = Palm(tile_size, x, y, map_sprites['palm_small'], 38)

                        if col == '0':
                            sprite = Palm(tile_size, x, y, map_sprites['palm_large'], 70)

                    if type == 'palm_bg':
                        sprite = Palm(tile_size, x, y, map_sprites['palm_bg'], 63)

                    sprite_group.add(sprite)

        return sprite_group

    def horizontal_collision(self):
        player = self.player.sprite
        player.accelerate()
        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.palm_fg_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False

        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.palm_fg_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.jump_available = player.set_jump_available
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

    def switch_tags(self):
        p1 = self.player.sprite
        for username, player in self.other_players.items():
            if self.player.sprite.rect.colliderect(player['sprite'].sprite.rect):
                if self.current_time - self.last_tag >= self.tag_cooldown:
                    if p1.is_tagged:
                        p1.is_tagged = False
                        player['player_object'].is_tagged = True
                    else:
                        p1.is_tagged = True
                        player['player_object'].is_tagged = False
                    self.last_tag = self.current_time
                    self.tag_sound.play()

    def get_screenshot(self, display_surface):
        try:
            if self.player.sprite.is_tagged:
                x = self.player.sprite.rect.x
                y = self.player.sprite.rect.y
            else:
                for username, player in self.other_players.items():
                    if player['player_object'].is_tagged:
                        x = player['player_object'].x
                        y = player['player_object'].y

            surface_width = display_surface.get_width()
            surface_height = display_surface.get_height()
            subsurface_width = 800
            subsurface_height = 450

            if x + subsurface_width > surface_width:
                x_offset = (surface_width - x - subsurface_width) - 80
            else:
                x_offset = - 80

            if y + subsurface_height > surface_height:
                y_offset = (surface_height - y - subsurface_height) - 50
            elif y < 0:
                y_offset = -y
            else:
                y_offset = - 50

            subsurface = display_surface.subsurface(pygame.Rect(x+x_offset, y+y_offset, subsurface_width, subsurface_height))
            pygame.image.save(subsurface, '../assets/end_screen.png')
        except Exception as e:
            print(e)

    def run(self, display_surface, net, token):
        # decoration sprites
        self.sky.draw(display_surface)
        self.clouds.draw(display_surface, 0)

        # terrain sprites
        self.palm_bg_sprites.update(0, 0)
        self.palm_fg_sprites.update(0, 0)
        self.palm_bg_sprites.draw(display_surface)
        self.palm_fg_sprites.draw(display_surface)
        self.terrain_sprites.draw(display_surface)
        self.grass_sprites.draw(display_surface)
        self.crate_sprites.draw(display_surface)
        self.power_sprites.update(0, 0)
        self.power_sprites.draw(display_surface)

        # player sprites
        if not self.game_ended:
            self.player.update(0,display_surface)
            self.horizontal_collision()
            self.vertical_collision()

        self.player.draw(display_surface)
        get_time = net.send_udp({'type': 'get_time'})
        self.tag_cooldown = get_time['cooldown']
        self.current_time = get_time['current_time']
        self.timer = get_time['timer']

        if self.other_players:
            if not self.game_ended:
                p1 = self.player.sprite

                update = net.send_udp({
                    'type': 'update',
                    'pos': (p1.rect.left, p1.rect.top),
                    'facing_right': p1.facing_right,
                    'username': self.username,
                    'token': token,
                    'direction': p1.direction.x,
                    'status': p1.status,
                    'is_tagged': p1.is_tagged,
                    'last_tag': self.last_tag,
                    'frame_index': p1.frame_index
                })

                current_time = pygame.time.get_ticks()
                since_last_update = (current_time - self.last_update) / 1000.0

                if self.since_last_update <= self.max_interpolation_delay:
                    for username, player in self.other_players.items():
                        estimated_position = self.interpolate(update[username]['pos'], player['pos'], since_last_update)
                        self.other_players[username]['pos'].x, self.other_players[username]['pos'].y = estimated_position

                for username, player in self.other_players.items():
                    player['player_object'].update(id=1, display_surface=display_surface, pos=player['pos'], update=update[username])
                    player['sprite'].draw(display_surface)
                self.last_update = pygame.time.get_ticks()

        # timer
        self.timer_sprite.update(self.timer)
        self.timer_sprite.draw(display_surface)
        self.switch_tags()
        self.manage_timer(display_surface)

    def interpolate(self, start, end, alpha):
        x = start[0]*(1-alpha) + start[1]*(alpha)
        y = start[1]*(1-alpha) + start[1]*(alpha)
        return (x, y)
