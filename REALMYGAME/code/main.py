from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites

from random import randint, choice

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Nick Chicken')
        self.clock = pygame.time.Clock()
        self.running = True

        #groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 200

        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 1000)
        self.spawn_positions = []

        # life
        self.max_health = 3
        self.player_health = 3
        self.delay_hit = 1500
        self.hit_time = pygame.time.get_ticks()

        # audio
        """
        self.shoot_sound = pygame.mixer.Sound(join(''))
        self.shoot_sound.set_volume(0.4)
        self.impact_sound = pygame.mixer.Sound(join(''))
        self.music = pygame.mixer.Sound(join(''))
        self.music.set_volume(0.4)
        self.music.play(loops = -1)
        """
        self.load_images()
        self.setup()
    
    def load_images(self):
        self.bullet_surf = get_image(pygame.image.load(join(current_dir, '..', 'assets', 'gun', 'bullet.png')), 0, 32, 32, 0.2, BLACK)

        self.full_heart_surf = get_image(pygame.image.load(join(current_dir, '..', 'assets', 'heart', 'full_heart.png')).convert_alpha(), 0, 16, 16, 3, BLACK)
        self.death_heart_surf = get_image(pygame.image.load(join(current_dir, '..', 'assets', 'heart', 'death_heart.png')).convert_alpha(), 0, 16, 16, 3, BLACK)

        folders = list(walk(join(current_dir, '..', 'assets', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join(current_dir, '..', 'assets', 'enemies', folder, 'down')):
                frame = 0
                self.enemy_frames[folder] = []
                for file_name in file_names: 
                    full_path = join(folder_path, file_name)
                    original_image = pygame.image.load(full_path).convert_alpha()
                    while frame < 6:
                        surf = get_image(original_image, frame, 64, 64, 1, BLACK)
                        self.enemy_frames[folder].append(surf)
                        frame += 1    


    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            #self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 10
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        map = load_pygame(join(current_dir, '..', 'assets', 'maps', 'map.tmx'))

        for x, y, image in  map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)
        
        for x, y, image in  map.get_layer_by_name('Collisions').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            if obj.name == 'Small_tree':
                CollisionSprite((obj.x, obj.y), obj.image, 'Small_tree', (self.all_sprites, self.collision_sprites))
            else: CollisionSprite((obj.x, obj.y), obj.image, 'Other objects', (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Col'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), 'Collision' , self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    #self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy()
                    bullet.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False) and pygame.time.get_ticks() - self.hit_time >= self.delay_hit:
            self.hit_time = pygame.time.get_ticks()
            self.player_health -= 1
            if self.player_health <= 0:
                self.running = False

    def draw_hearts(self):
        for heart in range(self.player_health):
            self.display_surface.blit(self.full_heart_surf, (heart * 50, 0))
        for heart in range(self.max_health - self.player_health):
            self.display_surface.blit(self.death_heart_surf, ((self.player_health + heart) * 50, 0))

    def run(self):
        while self.running:
            #dt
            dt = self.clock.tick(60) / 1000 # 60 FPS

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event: #pass
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)

            #update
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()

            #draw
            self.display_surface.fill(BLACK)
            self.all_sprites.draw(self.player.rect.center)
            self.draw_hearts()
            pygame.display.update()

        pygame.quit()   

if __name__ == '__main__':
    game = Game()
    game.run()