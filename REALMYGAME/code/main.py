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

        # text font
        self.font_size = 30
        self.font = pygame.font.Font(join(current_dir, '..', 'assets', 'fonts', 'Pixel.ttf'), self.font_size)

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
        
        self.shoot_sound = pygame.mixer.Sound(join(current_dir, '..', 'assets', 'sounds', 'shoot.wav'))
        self.shoot_sound.set_volume(0.1)
        self.impact_sound = pygame.mixer.Sound(join(current_dir, '..', 'assets', 'sounds', 'impact.wav'))
        self.impact_sound.set_volume(0.2)
        self.music = pygame.mixer.Sound(join(current_dir, '..', 'assets', 'sounds', 'beautiful_dream.wav'))
        self.music.set_volume(0.4)
        self.music.play(loops = -1)
        self.load_images()
        self.setup()

        # highscore
        self.score = 0
        self.highscore = 0  # Initialize highscore
        self.load_highscore()  # Load highscore from file


    def load_highscore(self):
        try:
            with open(join(current_dir, '..', 'highscore', 'highscore.txt'), 'r') as file:
                self.highscore = int(file.read())
        except FileNotFoundError:
            self.highscore = 0

    def save_highscore(self):
        with open(join(current_dir, '..', 'highscore', 'highscore.txt'), 'w') as file:
            file.write(str(self.highscore))
    
    def load_images(self):
        self.bullet_surf = get_image(pygame.image.load(join(current_dir, '..', 'assets', 'gun', 'bullet.png')), 0, 32, 32, 0.2, BLACK)

        self.full_heart_surf = get_image(pygame.image.load(join(current_dir, '..', 'assets', 'heart', 'full_heart.png')).convert_alpha(), 0, 16, 16, 3, BLACK)
        self.death_heart_surf = get_image(pygame.image.load(join(current_dir, '..', 'assets', 'heart', 'death_heart.png')).convert_alpha(), 0, 16, 16, 3, BLACK)

        folders = list(walk(join(current_dir, '..', 'assets', 'enemies')))[0][1]
        self.enemy_frames = {'Slime1': {'down':{'run':[], 'idle':[], 'death':[]}},
                             'Slime2': {'down':{'run':[], 'idle':[], 'death':[]}},
                             'Slime3': {'down':{'run':[], 'idle':[], 'death':[]}}}
        for folder in folders: # folder ở đây là tên enemy (ví dụ: 'Slime1')
            for anim_type in self.enemy_frames[folder]['down']:
                for folder_path, sub_folders, file_names in walk(join(current_dir, '..', 'assets', 'enemies', folder, 'down', anim_type)):
                    for file_name in file_names:
                        original_image = pygame.image.load(join(folder_path, file_name)).convert_alpha()
                        if anim_type == 'idle': max_frame = 6
                        elif anim_type == 'run': max_frame = 8
                        else: max_frame = 10
        
                        for frame in range(max_frame):
                            surf = get_image(original_image, frame, 64, 64, 1, BLACK)
                            self.enemy_frames[folder]['down'][anim_type].append(surf)


    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
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

    def bullet_collision(self, dt):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    for sprite in collision_sprites:
                        if sprite.alive:
                            self.impact_sound.play()
                            self.score += 1
                            sprite.destroy(dt)
                            bullet.kill()
                            break

    def player_collision(self):
        for sprite in pygame.sprite.spritecollide(self.player, self.enemy_sprites, False):
            if sprite.alive and pygame.time.get_ticks() - self.hit_time >= self.delay_hit:
                self.hit_time = pygame.time.get_ticks()
                self.player_health -= 1
                if self.player_health <= 0:
                    self.running = False

    def draw_hearts(self):
        for heart in range(self.player_health):
            self.display_surface.blit(self.full_heart_surf, (heart * 50, 0))
        for heart in range(self.max_health - self.player_health):
            self.display_surface.blit(self.death_heart_surf, ((self.player_health + heart) * 50, 0))

    def draw_score(self):
        score_surf = self.font.render('Score: ' + str(self.score), True, BLACK) # True for anti-aliasing
        score_rect = score_surf.get_rect()  # Get the rectangle for positioning
        score_rect.topright = (WINDOW_WIDTH - 20, 20)  
        self.display_surface.blit(score_surf, score_rect)


        highscore_surf = self.font.render('Highscore: ' + str(self.highscore), True, BLACK) 
        highscore_rect = highscore_surf.get_rect()  
        highscore_rect.topright = (WINDOW_WIDTH - 20, 60)  
        self.display_surface.blit(highscore_surf, highscore_rect)

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
            self.bullet_collision(dt)
            self.player_collision()

            if self.score > self.highscore:
                self.highscore = self.score
                self.save_highscore()

            #draw
            self.display_surface.fill(BLACK)
            self.all_sprites.draw(self.player.rect.center)
            self.draw_hearts()
            self.draw_score()
            pygame.display.update()

        pygame.quit()   

if __name__ == '__main__':
    game = Game()
    game.run()