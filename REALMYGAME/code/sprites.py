from settings import *
from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        #player connection
        self.player = player
        self.distance = 35
        self.player_direction = pygame.Vector2(1,0)

        #sprite setup
        super().__init__(groups)
        self.gun_surf = pygame.image.load(join(current_dir, '..', 'assets', 'gun', 'gun.png')).convert_alpha()
        self.image = get_image(self.gun_surf, 0, 128, 68, 0.15, BLACK)
        self.rect = self.image.get_rect(center = self.player.rect.center + self.player_direction * self.distance)

    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        #print(mouse_pos - player_pos)
        self.player_direction = (mouse_pos - player_pos).normalize() if (mouse_pos - player_pos) else (mouse_pos - player_pos)

    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 0.15)
        elif self.player_direction.y != -1: # y = -1 thi sung chia thang vao dau
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 0.15)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000 # thoi gian ton tai

        self.direction = direction
        self.speed = 200

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt # update vi tri bullet

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime: # neu ton tai lau hon self.lifetime thi cho bien mat
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, surf, player, groups):
        super().__init__(groups)