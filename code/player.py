import pygame
from game_data import players
from util import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self, id, pos, surface):
        super().__init__()
        self.import_assets()
        self.player_id = id
        self.frame_index = 0
        self.animation_speed = 0.30
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        self.is_tagged = False

        # movement
        self.direction = pygame.math.Vector2(0, 0)
        self.min_speed = 5
        self.max_speed = 10
        self.set_gravity = 1.5
        self.set_jump_available = 2
        self.acceleration = 0

        self.speed = self.min_speed
        self.gravity = self.set_gravity
        self.jump_speed = -1.5 * self.speed
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

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()

    def get_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def accelerate(self):
        if self.status == 'run' or self.status == 'jump':
            if self.speed < self.max_speed:
                self.acceleration += 0.01
            else:
                self.acceleration = 0
        else:
            if self.status == 'idle':
                if self.speed > self.min_speed:
                    self.acceleration -= 0.01
                else:
                    self.acceleration = 0
            else:
                if self.speed > self.min_speed:
                    self.acceleration -= 0.05
                else:
                    self.acceleration = 0

        self.speed += self.acceleration
        self.rect.x += self.speed * self.direction.x

        print(self.speed)

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
