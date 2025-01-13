from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        #camera offset
        self.offset = pygame.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        #zoom
        self.zoom_scale = 3
        self.internal_surf_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA) 
        self.internal_rect = self.internal_surf.get_rect(center = (self.half_w, self.half_h))
        self.internal_surf_size_vector = pygame.math.Vector2(self.internal_surf_size)

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - self.half_w)
        self.offset.y = -(target_pos[1] - self.half_h)

        self.internal_surf.fill(BLACK)

        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')]
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground')]

        for layer in [ground_sprites, object_sprites]:
            for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery):
                draw_pos = sprite.rect.topleft + self.offset
                self.internal_surf.blit(sprite.image, draw_pos)
        
        scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surf_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center = (self.half_w, self.half_h))

        self.display_surface.blit(scaled_surf, scaled_rect)

