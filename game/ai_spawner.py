import random
import pygame

from game.standard_monster import StandardMonster
from game.tough_monster import ToughMonster


class MonsterType:
    def __init__(self, monster_id, monster_points):
        self.points = monster_points
        self.id = monster_id


class AISpawner:

    def __init__(self, monsters, all_monster_sprites, tiled_level):
        self.monsters = monsters
        self.tiled_level = tiled_level

        self.available_ai_types = {StandardMonster.monster_id: MonsterType(StandardMonster.monster_id,
                                                                           StandardMonster.point_cost),
                                   ToughMonster.monster_id: MonsterType(ToughMonster.monster_id,
                                                                        ToughMonster.point_cost)}

        self.monster_image_dict = {StandardMonster.monster_id: pygame.image.load(StandardMonster.image_path),
                                   ToughMonster.monster_id: pygame.image.load(ToughMonster.image_path)}

        self.all_monster_sprites = all_monster_sprites
        
    def update(self):
        if len(self.monsters) < 6:
            self.spawn_new_ai()

    def spawn_new_ai(self):
        new_monster = self.pick_new_monster()
        self.monsters.append(new_monster)

    def pick_new_monster(self):
        ai_type_id = random.choice(list(self.available_ai_types.keys()))
        new_monster = None
        if ai_type_id == StandardMonster.monster_id:
            new_monster = StandardMonster(self.get_random_start_pos(), self.monster_image_dict,
                                          self.available_ai_types, self.all_monster_sprites, self.tiled_level)
        elif ai_type_id == ToughMonster.monster_id:
            new_monster = ToughMonster(self.get_random_start_pos(), self.monster_image_dict,
                                       self.available_ai_types, self.all_monster_sprites, self.tiled_level)
       
        return new_monster

    def get_random_start_pos(self):
        random_start_tile = random.choice(self.tiled_level.walkable_tiles)
        return random_start_tile.world_position
