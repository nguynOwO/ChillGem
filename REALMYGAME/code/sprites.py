from settings import *
from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, name, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        
        # hit box
        if name == 'Small_tree': 
            self.rect = self.rect.inflate(-10, -13) 

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        #player connection
        self.player = player
        self.distance = 20
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
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player 
        self.alive = True

        #image
        self.frames, self.frame_index, self.frame_death_index = frames, 0, 0
        self.image = self.frames['down']['idle'][self.frame_index]
        self.animation_speed = 6
        self.animation_death_speed = 10

        #rect
        self.rect = self.image.get_rect(center = pos)
        self.hitbox_rect = self.rect.inflate(-24, -24)

        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2(0, 0)
        self.speed = 65

        # timer
        self.death_time = 0
        self.death_duration = 1000

    def animate(self, dt, alive):
        if alive: 
            self.frame_index += self.animation_speed * dt
            self.image = self.frames['down']['idle'][int(self.frame_index) % len(self.frames['down']['idle'])]
        else:
            # animation death
            self.frame_death_index += self.animation_death_speed * dt
            #print(int(self.frame_death_index))
            self.image = self.frames['down']['death'][int(self.frame_death_index) if int(self.frame_death_index) < 10 else 9]

    def move(self, dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize() if (player_pos - enemy_pos) else (player_pos - enemy_pos)

        # update the rect pos + collision
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center
        
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    elif self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    elif self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom

    def destroy(self, dt):
        # timer
        self.alive = False
        self.death_time = pygame.time.get_ticks()

    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt, self.alive)
        else: 
            self.animate(dt, self.alive)
            self.death_timer()
