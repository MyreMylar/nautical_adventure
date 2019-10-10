from game.base_monster import BaseMonster


class StandardMonster(BaseMonster):
    monster_id = "standard"
    image_path = "images/sailing_ship_2.png"
    point_cost = 1

    def __init__(self, start_pos, image_dictionary, monster_type_dict, all_monster_sprites, tiled_level):
          
        image = image_dictionary[StandardMonster.monster_id]
        monster_type = monster_type_dict[StandardMonster.monster_id]
        super().__init__(start_pos, StandardMonster.monster_id, image,
                         monster_type.points, all_monster_sprites, tiled_level)

        self.cash_value = 30
        self.idle_move_speed = self.set_average_speed(35)
        self.attack_move_speed = self.set_average_speed(75)
        self.move_speed = self.idle_move_speed
        self.health = 200
        self.attack_damage = 20
        self.attack_time_delay = 3.0
