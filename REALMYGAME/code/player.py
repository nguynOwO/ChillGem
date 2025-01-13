# player.py
import pygame
from settings import *
from os import walk

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index, self.status = 'down', 0, 'idle'
        self.original_image = pygame.image.load(join(current_dir, '..', 'assets','player','down','idle','idle.png')).convert_alpha()
        self.image = get_image(self.original_image, 3, 32, 32, 1.25, BLACK)
        self.rect = self.image.get_rect(center = pos)
        self.hitbox_rect = self.rect.inflate(-18.75, -37.75)

        #movement
        self.direction = pygame.Vector2()
        self.speed = 100
        self.collision_sprites = collision_sprites

    def load_images(self):
        self.frames = {'left': {'run':[], 'idle':[]}, 'right': {'run':[], 'idle':[]}, 'up': {'run':[], 'idle':[]}, 'down':{'run':[], 'idle':[]}}
        
        for state in self.frames.keys():
            for anim_type in self.frames[state].keys():
                for folder_path, sub_folders, file_names in walk(join(current_dir, '..', 'assets', 'player', state, anim_type)):
                    if file_names:
                        frame = 0
                        for file_name in file_names:
                            if file_name.endswith(('.png', '.jpg')): # Đảm bảo chỉ load file ảnh
                                original_image = pygame.image.load(join(folder_path, file_name)).convert_alpha()
                                while frame < 5:
                                    surf = get_image(original_image, frame, 32, 32, 1.25, BLACK)
                                    self.frames[state][anim_type].append(surf)
                                    frame += 1


    def input(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int((keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a]))
        self.direction.y = int((keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w]))
        self.direction = self.direction.normalize() if self.direction else self.direction
    
        if keys[pygame.K_LSHIFT]: 
            self.speed = 200
            self.frame_index += 10 * dt
        else: self.speed = 100

    def move(self, dt):
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

    def animate(self, dt):
        #state
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = 'idle'
        else:
            self.status = 'run'

        if self.direction.x > 0:
            self.state = 'right'
        elif self.direction.x < 0:
            self.state = 'left'
        elif self.direction.y > 0:
            self.state = 'down'
        elif self.direction.y < 0:
            self.state = 'up'

        #animate
        if self.frames[self.state][self.status]:
            self.frame_index += 5 * dt
            self.image = self.frames[self.state][self.status][int(self.frame_index) % len(self.frames[self.state][self.status])]

    def update(self, dt):
        self.input(dt)
        self.move(dt)
        self.animate(dt)
        #print(f"Player Rect: {self.rect}")