import pygame
import game_data
from settings import tile_size
from tile import StaticTile, Coin, Crate, Palm
from util import import_csv_layout, import_cut_graphics, read_pos, make_pos
from decorations import Sky, Clouds
from player import Player, ParticleEffect

class Map0:
    def __init__(self, surface, net):
        self.display_surface = surface
        self.world_shift_x = 0
        self.net = net

        self.start_pos = read_pos(self.net.get_pos())

        # player setup
        self.current_x = 0
        self.player = pygame.sprite.GroupSingle()
        self.player2 = pygame.sprite.GroupSingle()
        self.player2_pos = pygame.math.Vector2(0, 0)
        self.player_setup()

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # terrain
        terrain_layout = import_csv_layout(game_data.map0['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout,
                                                      'terrain')

        # grass
        grass_layout = import_csv_layout(game_data.map0['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        # crates
        crate_layout = import_csv_layout(game_data.map0['crate'])
        self.crate_sprites = self.create_tile_group(crate_layout, 'crate')

        # power
        power_layout = import_csv_layout(game_data.map0['power'])
        self.power_sprites = self.create_tile_group(power_layout, 'power')

        # palm fg
        palm_fg_layout = import_csv_layout(game_data.map0['palm_fg'])
        self.palm_fg_sprites = self.create_tile_group(palm_fg_layout,
                                                      'palm_fg')

        # palm bg
        palm_bg_layout = import_csv_layout(game_data.map0['palm_bg'])
        self.palm_bg_sprites = self.create_tile_group(palm_bg_layout,
                                                      'palm_bg')

        # decoration
        self.sky = Sky(10)
        level_width = len(terrain_layout[0]) * tile_size
        self.clouds = Clouds(400, level_width, 20)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, col in enumerate(row):
                if col != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_path = '../assets/terrain/terrain_tiles.png'
                        terrain_tile_list = import_cut_graphics(terrain_path)
                        tile_surface = terrain_tile_list[int(col)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'grass':
                        grass_path = '../assets/decoration/grass/grass.png'
                        grass_tile_list = import_cut_graphics(grass_path)
                        grass_surface = grass_tile_list[int(col)]
                        sprite = StaticTile(tile_size, x, y, grass_surface)

                    if type == 'crate':
                        crate_path = '../assets/terrain/crate.png'
                        sprite = Crate(tile_size, x, y, crate_path)

                    if type == 'power':
                        if col == '1':
                            jump_path = '../assets/coins/silver/'
                            sprite = Coin(tile_size, x, y, jump_path)

                        if col == '0':
                            run_path = '../assets/coins/gold/'
                            sprite = Coin(tile_size, x, y, run_path)

                    if type == 'palm_fg':
                        if col == '5':
                            palm_path = '../assets/terrain/palm_small/'
                            sprite = Palm(tile_size, x, y, palm_path, 38)

                        if col == '0':
                            palm_path = '../assets/terrain/palm_large/'
                            sprite = Palm(tile_size, x, y, palm_path, 70)

                    if type == 'palm_bg':
                        palm_path = '../assets/terrain/palm_bg/'
                        sprite = Palm(tile_size, x, y, palm_path, 63)

                    sprite_group.add(sprite)

        return sprite_group

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos += pygame.math.Vector2(-10, -15)
        else:
            pos += pygame.math.Vector2(10, -15)

        jump_particles_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particles_sprite)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(-10, -15)
            else:
                offset = pygame.math.Vector2(10, -15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom + offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def horizontal_collision(self):
        player = self.player.sprite
        # player.rect.x += player.direction.x * player.speed
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

    def player_setup(self):
        player1 = Player(1, self.start_pos, self.display_surface, self.create_jump_particles)
        player2 = Player(2, (100, 100), self.display_surface, self.create_jump_particles)
        self.player.add(player1)
        self.player2.add(player2)

    def run(self):
        # decoration sprites
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, 0)

        # terrain sprites
        self.terrain_sprites.draw(self.display_surface)
        self.palm_bg_sprites.update(0, 0)
        self.palm_fg_sprites.update(0, 0)
        self.palm_bg_sprites.draw(self.display_surface)
        self.palm_fg_sprites.draw(self.display_surface)
        self.grass_sprites.draw(self.display_surface)
        self.crate_sprites.draw(self.display_surface)
        self.power_sprites.update(0, 0)
        self.power_sprites.draw(self.display_surface)

        # player sprites
        self.player.update(0)
        self.player.draw(self.display_surface)
        self.horizontal_collision()
        self.vertical_collision()
        self.dust_sprite.update(self.world_shift_x)
        self.dust_sprite.draw(self.display_surface)
        self.get_player_on_ground()
        self.create_landing_dust()

        # transmit and receive positions
        p1_rect = self.player.sprite.rect
        p2_rect = self.player2.sprite.rect

        p2_pos = read_pos(self.net.send(make_pos((p1_rect.left,
                                                  p1_rect.top))))

        self.player2_pos.x, self.player2_pos.y = p2_pos[0], p2_pos[1]
        self.player2.update(1, self.player2_pos)
        self.player2.draw(self.display_surface)
