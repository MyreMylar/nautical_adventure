import pygame


class PickUpSpawner:
    def __init__(self, pick_ups, all_pick_up_sprites):
        self.pick_ups = pick_ups
        self.all_pick_up_sprites = all_pick_up_sprites
        self.flotsam_image = pygame.image.load("images/pick_ups/flotsam.png")

    def try_spawn(self, spawn_position):
        self.pick_ups.append(PickUp(spawn_position, self.flotsam_image, "flotsam", self.all_pick_up_sprites))
       
        
class PickUp:
    def __init__(self, start_pos, image, type_name, all_pick_up_sprites):
        self.world_position = [start_pos[0], start_pos[1]]
        self.type_name = type_name
        self.image = image
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.image
        self.sprite.rect = self.image.get_rect()  
        self.sprite.rect.center = start_pos

        self.position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]

        self.all_pick_up_sprites = all_pick_up_sprites
        self.all_pick_up_sprites.add(self.sprite)
        self.should_die = False

    def update_movement_and_collision(self, player, tiled_level):
        self.position[0] = self.world_position[0] - tiled_level.position_offset[0]
        self.position[1] = self.world_position[1] - tiled_level.position_offset[1]
        self.sprite.rect.center = self.position
        if player.test_pick_up_collision(self.sprite.rect):
            self.should_die = True
            if self.type_name == "flotsam":
                player.add_random_cargo()
            self.all_pick_up_sprites.remove(self.sprite)
