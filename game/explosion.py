import random
import pygame

from game.damage import Damage


class Explosion:
    def __init__(self, start_pos, explosion_sheet, size, damage_amount, damage_type):

        self.radius = size
        self.collide_radius = self.radius
        self.explosion_sheet = explosion_sheet
        self.explosion_frames = 16
        self.explosion_images = []
        random_explosion_int = random.randrange(0, 512, 64)
        for i in range(0, self.explosion_frames):
            x_start_index = (i * 64)
            explosion_frame = self.explosion_sheet.subsurface(pygame.Rect(x_start_index + 1,
                                                                          random_explosion_int + 1, 62, 62))
            explosion_frame = pygame.transform.scale(explosion_frame, (self.radius*2, self.radius*2))
            self.explosion_images.append(explosion_frame)
        self.sprite = pygame.sprite.Sprite()      
        self.sprite.image = self.explosion_images[0]
                
        self.sprite.rect = self.explosion_images[0].get_rect()
        self.sprite.rect.center = start_pos

        self.position = [float(self.sprite.rect.center[0]),
                         float(self.sprite.rect.center[1])]
        
        self.should_die = False
        self.life_time = 0.45
        self.time = self.life_time
        self.frame_time = self.life_time / self.explosion_frames
        self.frame = 1

        self.damage = Damage(damage_amount, damage_type)
        
    def update_sprite(self, all_explosion_sprites, time_delta):
        self.time -= time_delta
        if self.time < 0.0:
            self.should_die = True

        if self.frame < self.explosion_frames and (self.life_time - self.time) > (self.frame_time * self.frame):
            self.sprite.image = self.explosion_images[self.frame]
            self.frame += 1

        all_explosion_sprites.add(self.sprite)
            
        return all_explosion_sprites

    def update_movement_and_collision(self):
        pass
