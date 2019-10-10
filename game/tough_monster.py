from game.base_monster import BaseMonster


class ToughMonster(BaseMonster):

    monster_id = "tough"
    image_path = "images/sailing_ship_3.png"
    point_cost = 5

    def __init__(self, start_pos, image_dictionary, monster_type_dict, all_monster_sprites, play_area):
          
        image = image_dictionary[ToughMonster.monster_id]
        monster_type = monster_type_dict[ToughMonster.monster_id]
        super().__init__(start_pos, ToughMonster.monster_id, image, monster_type.points, all_monster_sprites, play_area)
        self.cash_value = 60
        self.idle_move_speed = self.set_average_speed(45)
        self.attack_move_speed = self.set_average_speed(100)
        self.move_speed = self.idle_move_speed

        self.health = 400
        self.attack_damage = 40
        self.attack_time_delay = 1.5
