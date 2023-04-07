import pygame
from game_data import players
from util import import_folder

class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, type):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.5

        if type == 'jump':
            self.frames = import_folder('../assets/character_pirate/dust_particles/jump/')
        if type == 'land':
            self.frames = import_folder('../assets/character_pirate/dust_particles/land/')

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift

class Player(pygame.sprite.Sprite):
    def __init__(self, id, pos, surface, create_jump_particles):
        super().__init__()
        self.import_assets()
        self.player_id = id
        self.frame_index = 0
        self.animation_speed = 0.20
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        self.is_tagged = False

        # dust particles
        self.import_dust_run_assets()
        self.dust_frame_index = 0
        self.dust_animation_speed = 0.15
        self.display_surface = surface
        self.create_jump_particles = create_jump_particles

        # movement
        self.direction = pygame.math.Vector2(0, 0)
        self.min_speed = 7
        self.max_speed = 11
        self.set_gravity = 1.5
        self.set_jump_available = 2
        self.set_acceleration = 0.01
        self.max_acceleration = 2
        self.set_deceleration = 0.2
        self.max_jump_speed = -25
        self.min_jump_speed = -17

        self.acceleration = 0
        self.speed = self.min_speed
        self.gravity = self.set_gravity
        self.jump_speed = -3 * self.speed
        self.jump_available = self.set_jump_available

        # status
        self.status = 'idle'
        self.facing_right = True
        self.on_ground = True
        self.on_ceiling = False
        self.on_right = False
        self.on_left = False

    def import_assets(self):
        # path = players[self.player_id].path
        path = '../assets/character_pirate/'
        self.animations = {'idle': [], 'fall': [], 'run': [], 'jump': []}

        for animation in self.animations.keys():
            full_path = path + animation
            self.animations[animation] = import_folder(full_path)

        self.animations['run_stop'] = import_folder(path + 'run')

    def import_dust_run_assets(self):
        self.dust_run_assets = import_folder('../assets/character_pirate/dust_particles/run/')

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False)

        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif self.on_ceiling and self.on_right:
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif self.on_ceiling and self.on_left:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif self.on_ceiling:
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    def run_dust_animation(self):
        if self.status == 'run' and self.on_ground:
            self.dust_frame_index += self.dust_animation_speed
            if self.dust_frame_index >= len(self.dust_run_assets):
                self.dust_frame_index = 0

            dust_particle = self.dust_run_assets[int(self.dust_frame_index)]

            if self.facing_right:
                self.display_surface.blit(dust_particle, self.rect.bottomleft - pygame.math.Vector2(9, 9))
            else:
                self.display_surface.blit(pygame.transform.flip(dust_particle, True, False), self.rect.bottomright - pygame.math.Vector2(9, 9))

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.status = 'run'
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.status = 'run'
            self.direction.x = -1
            self.facing_right = False
        elif self.speed > self.min_speed:
            self.status = 'run_stop'
        else:
            if self.direction.y == 0:
                self.status = 'idle'

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.jump_speed = -2.5 * self.speed
            if self.jump_speed < self.max_jump_speed:
                self.jump_speed = self.max_jump_speed
            if self.jump_speed > self.min_jump_speed:
                self.jump_speed = self.min_jump_speed
            self.jump()
            if self.jump_speed < (self.max_jump_speed - self.min_jump_speed) / 2 + self.min_jump_speed:
                self.create_jump_particles(self.rect.midbottom)

    def get_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'

        if self.speed < self.min_speed and self.direction.y == 0:
            self.status = 'idle'

    def accelerate(self):
        if self.status == 'run':
            self.acceleration += self.set_acceleration

        if self.status == 'fall':
            self.acceleration -= self.set_acceleration/100

        if self.status == 'idle':
            self.direction.x = 0
            self.acceleration = 0

        if self.status == 'run_stop':
            self.acceleration -= self.set_deceleration

        if self.acceleration > self.max_acceleration:
            self.acceleration = 1

        if self.acceleration < -self.max_acceleration:
            self.acceleration = 0

        self.speed += self.acceleration

        if self.speed > self.max_speed:
            self.speed = self.max_speed

        if self.speed < self.min_speed:
            self.speed = self.min_speed

        if self.status == 'fall':
            self.speed = self.speed - 1

        self.rect.x += self.speed * self.direction.x

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
        if self.speed > (self.max_speed - self.min_speed)/2 + self.min_speed:
            self.run_dust_animation()
