import math
import random

from game.tile import *
from game.village_tile import *


class TiledLevel:
    def __init__(self, level_tile_size, all_tile_sprites, all_top_tile_sprites, screen_data, all_trade_goods):

        self.initial_screen_offset = [0, 0]
        self.position_offset = [0, 0]
        self.current_centre_position = [100000000, 111111111111]

        self.file_name = "data/level.csv"
        self.screen_data = screen_data

        self.all_tile_sprites = all_tile_sprites
        self.all_top_tile_sprites = all_top_tile_sprites

        self.tile_map = self.load_tile_table("images/tiles/tile_map.png", 64, 64, False)
        
        self.zero_tile_x = 0
        self.zero_tile_y = 0
        self.end_tile_x = 0
        self.end_tile_y = 0

        self.playerStart = [0, 0]
        #: :type: list of list
        self.top_tile_grid = []
        #: :type: list of list
        self.tile_grid = []
        self.tiles = []
        self.collidable_tiles = []
        self.walkable_tiles = []

        self.villages = []
        self.ai_spawns = []

        self.level_tile_size = level_tile_size  # 64,64
        self.level_pixel_size = [self.level_tile_size[0] * 64, self.level_tile_size[1] * 64]

        self.village_names = ["Toyogo", "Fallu", "Husu", "Jupi", "Lesusu", "Simina",
                              "Las Elbos", "Jegaba", "Letso", "Tumi", "Yun", "Sela", "Galu"]
        self.exports = all_trade_goods

        for tileX in range(0, self.level_tile_size[0]):
            column = []
            top_column = []
            for tile_y in range(0, self.level_tile_size[1]):
                column.append(None)
                top_column.append(None)
            self.tile_grid.append(column)
            self.top_tile_grid.append(top_column)
    
        self.initial_offset = True

        self.all_tile_data = {}
        tile_data_files = [file for file in os.listdir("data/tiles/") if os.path.isfile(os.path.join("data/tiles/",
                                                                                                     file))]

        self.default_tiles = []
        for file_name in tile_data_files:
            new_tile_data = TileData(os.path.join("data/tiles/", file_name), self.tile_map)
            new_tile_data.load_tile_data()
            self.all_tile_data[new_tile_data.tile_id] = new_tile_data
            if new_tile_data.tile_id.find("grass_tile") != -1:
                self.default_tiles.append(new_tile_data)

    def clear_level_to_default_tile(self):
        for x in range(0, self.level_tile_size[0]):
            for y in range(0, self.level_tile_size[1]):
                x_centre = 32 + (x * 64)
                y_centre = 32 + (y * 64)
                default_tile = Tile([x_centre, y_centre], 0, random.choice(self.default_tiles), 0)
                self.tiles.append(default_tile)
                self.walkable_tiles.append(default_tile)
                self.tile_grid[x][y] = default_tile

    def update_offset_position(self, centre_position, all_tile_sprites, all_top_tile_sprites):
        should_update = False
        self.current_centre_position = centre_position
        x_offset = int(self.current_centre_position[0] - self.initial_screen_offset[0])
        y_offset = int(self.current_centre_position[1] - self.initial_screen_offset[1])

        if x_offset <= 0:
            x_offset = 0
        if x_offset >= int(self.level_pixel_size[0] - self.screen_data.play_area[0]):
            x_offset = int(self.level_pixel_size[0] - self.screen_data.play_area[0])

        if y_offset <= 0:
            y_offset = 0
        if y_offset >= int(self.level_pixel_size[1] - self.screen_data.play_area[1]):
            y_offset = int(self.level_pixel_size[1] - self.screen_data.play_area[1])
            
        if self.initial_offset or not (x_offset == self.position_offset[0] and y_offset == self.position_offset[1]):
            if self.initial_offset:
                self.initial_offset = False
            self.position_offset = [x_offset, y_offset]

            screen_tile_width = int(self.screen_data.play_area[0] / 64) + 1
            screen_tile_height = int(self.screen_data.play_area[1] / 64) + 2

            old_zero_tile_x = self.zero_tile_x
            old_zero_tile_y = self.zero_tile_y

            self.zero_tile_x = int(x_offset / 64)
            self.zero_tile_y = int(y_offset / 64)

            if self.zero_tile_x != old_zero_tile_x or self.zero_tile_y != old_zero_tile_y:
                all_tile_sprites.empty()
                all_top_tile_sprites.empty()
                self.end_tile_x = self.zero_tile_x + screen_tile_width
                self.end_tile_y = self.zero_tile_y + screen_tile_height

                if self.end_tile_x >= len(self.tile_grid):
                    self.end_tile_x = len(self.tile_grid)
                if self.end_tile_y >= len(self.tile_grid[0]):
                    self.end_tile_y = len(self.tile_grid[0])
                
                for tileX in range(self.zero_tile_x, self.end_tile_x):
                    for tileY in range(self.zero_tile_y, self.end_tile_y):
                        tile = self.tile_grid[tileX][tileY]
                        if tile is None:
                            print("No tile at grid: " + str(tileX) + ", " + str(tileY))
                        else:
                            tile.update_offset_position(self.position_offset, self.screen_data)
                            all_tile_sprites.add(tile.sprite)
                        top_tile = self.top_tile_grid[tileX][tileY]
                        if top_tile is not None:
                            top_tile.update_offset_position(self.position_offset, self.screen_data)
                            all_top_tile_sprites.add(top_tile.sprite)
            else:
                for tileX in range(self.zero_tile_x, self.end_tile_x):
                    for tileY in range(self.zero_tile_y, self.end_tile_y):
                        tile = self.tile_grid[tileX][tileY]
                        tile.update_offset_position(self.position_offset, self.screen_data)
                        
                        top_tile = self.top_tile_grid[tileX][tileY]
                        if top_tile is not None:
                            top_tile.update_offset_position(self.position_offset, self.screen_data)

            for spawn in self.ai_spawns:
                spawn.update_offset_position(self.position_offset)

        return should_update

    def draw_tile_collision_shapes(self, screen):
        for tileX in range(self.zero_tile_x, self.end_tile_x):
            for tileY in range(self.zero_tile_y, self.end_tile_y):
                tile = self.tile_grid[tileX][tileY]
                if tile is not None:
                    tile.drawCollisionShapes(screen)

    def get_random_village_name(self):
        random_name = "Mystery Village"
        if len(self.village_names) > 0:
            name_to_pick = random.randint(0, len(self.village_names) - 1)
            random_name = self.village_names[name_to_pick]
            self.village_names.remove(random_name)
        return random_name

    def get_random_export_name(self):
        random_name = "Mystery Village"
        if len(self.exports) > 0:
            name_to_pick = random.randint(0, len(self.exports)-1)
            random_name = self.exports[name_to_pick].name
        return random_name

    def save_tiles(self):
        with open(self.file_name, "w", newline='') as tileFile:
            writer = csv.writer(tileFile)
            for tile in self.tiles:
                if tile.tile_id.find("village") != -1:
                    writer.writerow(["tile", tile.tile_id, str(tile.world_position[0]), str(tile.world_position[1]),
                                     str(tile.angle), str(tile.layer), tile.name, tile.export])
                else:
                    writer.writerow(["tile", tile.tile_id, str(tile.world_position[0]), str(tile.world_position[1]),
                                     str(tile.angle), str(tile.layer)])

    def load_tiles(self):
        if os.path.isfile(self.file_name):
            self.tiles[:] = []
            self.collidable_tiles[:] = []
            self.walkable_tiles[:] = []
            
            with open(self.file_name, "r") as tileFile:
                reader = csv.reader(tileFile)
                for line in reader:
                    line_type = line[0]
                    
                    if line_type == "tile":
                        tile_id = line[1]
                        tile_x_pos = int(line[2])
                        tile_y_pos = int(line[3])
                        tile_angle = int(line[4])
                        tile_layer = 0
                        if len(line) == 6:
                            tile_layer = int(line[5])

                        if tile_id.find("village") != -1:
                            village_name = line[6]
                            main_export = line[7]
                            loaded_tile = VillageTile([tile_x_pos, tile_y_pos], tile_angle,
                                                      self.all_tile_data[tile_id], tile_layer,
                                                      village_name, main_export, self.exports)
                        else:
                            loaded_tile = Tile([tile_x_pos, tile_y_pos], tile_angle,
                                               self.all_tile_data[tile_id], tile_layer)
                        self.tiles.append(loaded_tile)

                        if tile_layer == 0:
                            self.tile_grid[int((tile_x_pos - 32) / 64)][int((tile_y_pos - 32) / 64)] = loaded_tile
                            if loaded_tile.collidable:
                                self.collidable_tiles.append(loaded_tile)
                            else:
                                self.walkable_tiles.append(loaded_tile)
                        elif tile_layer == 1:
                            self.top_tile_grid[int((tile_x_pos - 32) / 64)][int((tile_y_pos - 32) / 64)] = loaded_tile

                        if tile_id.find("village") != -1:
                            self.villages.append(loaded_tile)
        else:
            self.clear_level_to_default_tile()

    def find_player_start(self):
        player_start = [0, 0]
        shortest_distance = 100000
        world_centre = [self.level_pixel_size[0] / 2, self.level_pixel_size[1] / 2]
        screen_centre = [self.screen_data.play_area[0] / 2, self.screen_data.play_area[1] / 2]
        for tile in self.walkable_tiles:
            x_dist = float(world_centre[0]) - float(tile.world_position[0])
            y_dist = float(world_centre[1]) - float(tile.world_position[1])
            distance = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
            if distance < shortest_distance:
                shortest_distance = distance
                
                player_start[0] = tile.world_position[0]
                player_start[1] = tile.world_position[1]

        self.playerStart = player_start
        
        self.initial_screen_offset[0] = screen_centre[0]
        self.initial_screen_offset[1] = screen_centre[1]
        
        x_offset = (world_centre[0] - self.initial_screen_offset[0])
        y_offset = (world_centre[1] - self.initial_screen_offset[1])

        self.position_offset = [x_offset, y_offset]
        return player_start

    def get_tile_data_at_pos(self, click_pos, layer):
        for tileX in range(self.zero_tile_x, self.end_tile_x):
            for tileY in range(self.zero_tile_y, self.end_tile_y):
                if layer == 0:
                    tile = self.tile_grid[tileX][tileY]
                    tile_screen_min = [(tileX*64) - self.position_offset[0], (tileY * 64) - self.position_offset[1]]
                    tile_screen_max = [(tileX*64) + 64 - self.position_offset[0],
                                       (tileY * 64) + 64 - self.position_offset[1]]
                    if tile_screen_min[0] <= click_pos[0] and tile_screen_min[1] <= click_pos[1]:
                        if tile_screen_max[0] > click_pos[0] and tile_screen_max[1] > click_pos[1]:
                            if tile is not None:
                                return [tile.sprite.rect, tile.tile_image, tile.tile_id, False, tile]
                            else:
                                return [pygame.Rect(tile_screen_min[0], tile_screen_min[1],
                                                    64, 64), None, "", False, None]
                if layer == 1:
                    tile = self.top_tile_grid[tileX][tileY]
                    tile_screen_min = [(tileX*64) - self.position_offset[0], (tileY * 64) - self.position_offset[1]]
                    tile_screen_max = [(tileX*64) + 64 - self.position_offset[0],
                                       (tileY * 64) + 64 - self.position_offset[1]]
                    if tile_screen_min[0] <= click_pos[0] and tile_screen_min[1] <= click_pos[1]:
                        if tile_screen_max[0] > click_pos[0] and tile_screen_max[1] > click_pos[1]:
                            if tile is not None:
                                return [tile.sprite.rect, tile.tileImage, tile.tileID, False, tile]
                            else:
                                return [pygame.Rect(tile_screen_min[0], tile_screen_min[1],
                                                    64, 64), None, "", False, None]
                    
        return [pygame.Rect(0, 0, 0, 0), None, "", False, None]

    def set_tile_at_pos(self, click_pos, tile_id, tile_angle, layer):
        tile_to_set = None
        tile_click_x = 0
        tile_click_y = 0
        for tileX in range(self.zero_tile_x, self.end_tile_x):
            for tileY in range(self.zero_tile_y, self.end_tile_y):
                if layer == 0:
                    tile = self.tile_grid[tileX][tileY]
                    tile_screen_min = [(tileX*64) - self.position_offset[0], (tileY * 64) - self.position_offset[1]]
                    tile_screen_max = [(tileX*64) + 64 - self.position_offset[0],
                                       (tileY * 64) + 64 - self.position_offset[1]]
                    if tile_screen_min[0] <= click_pos[0] and tile_screen_min[1] <= click_pos[1]:
                        if tile_screen_max[0] > click_pos[0] and tile_screen_max[1] > click_pos[1]:
                            tile_to_set = tile
                            tile_click_x = tileX
                            tile_click_y = tileY
                            break
                if layer == 1:
                    tile = self.top_tile_grid[tileX][tileY]
                    tile_screen_min = [(tileX*64) - self.position_offset[0], (tileY * 64) - self.position_offset[1]]
                    tile_screen_max = [(tileX*64) + 64 - self.position_offset[0],
                                       (tileY * 64) + 64 - self.position_offset[1]]
                    if tile_screen_min[0] <= click_pos[0] and tile_screen_min[1] <= click_pos[1]:
                        if tile_screen_max[0] > click_pos[0] and tile_screen_max[1] > click_pos[1]:
                            tile_to_set = tile
                            tile_click_x = tileX
                            tile_click_y = tileY
                            break
                        
        if tile_to_set is not None:
            if layer == 0:
                if tile_to_set.collidable:
                    self.collidable_tiles.remove(tile_to_set)
                else:
                    self.walkable_tiles.remove(tile_to_set)
            
            self.tiles.remove(tile_to_set)

            if tile_to_set.tile_id.find("village") != -1:
                self.villages.remove(tile_to_set)

            if tile_id.find("village") != -1:
                new_tile = VillageTile(tile_to_set.world_position, tile_angle,
                                       self.all_tile_data[tile_id], layer, self.get_random_village_name(),
                                       self.get_random_export_name(), self.exports)
            else:
                new_tile = Tile(tile_to_set.world_position, tile_angle, self.all_tile_data[tile_id], layer)
            self.tiles.append(new_tile)

            if tile_id.find("village") != -1:
                self.villages.append(new_tile)

            tile_x = int((new_tile.world_position[0] - 32) / 64)
            tile_y = int((new_tile.world_position[1] - 32) / 64)
            if layer == 0:
                self.tile_grid[tile_x][tile_y] = new_tile
                if new_tile.collidable:
                    self.collidable_tiles.append(new_tile)
                else:
                    self.walkable_tiles.append(new_tile)
            if layer == 1:
                self.top_tile_grid[tile_x][tile_y] = new_tile
        else:
            new_tile_world_position = [(tile_click_x*64)+32, (tile_click_y*64)+32]
            if tile_id.find("village") != -1:
                new_tile = VillageTile(new_tile_world_position, tile_angle,
                                       self.all_tile_data[tile_id],
                                       layer, self.get_random_village_name(),
                                       self.get_random_export_name(), self.exports)
            else:
                new_tile = Tile(new_tile_world_position, tile_angle, self.all_tile_data[tile_id], layer)
            self.tiles.append(new_tile)

            if tile_id.find("village") != -1:
                self.villages.append(new_tile)

            tile_x = int((new_tile.world_position[0] - 32) / 64)
            tile_y = int((new_tile.world_position[1] - 32) / 64)
            if layer == 0:
                self.tile_grid[tile_x][tile_y] = new_tile
                if new_tile.collidable:
                    self.collidable_tiles.append(new_tile)
                else:
                    self.walkable_tiles.append(new_tile)
            if layer == 1:
                self.top_tile_grid[tile_x][tile_y] = new_tile

        self.all_tile_sprites.empty()
        for tileX in range(self.zero_tile_x, self.end_tile_x):
            for tileY in range(self.zero_tile_y, self.end_tile_y):
                tile = self.tile_grid[tileX][tileY]
                if tile is None:
                    print("No tile at grid: " + str(tileX) + ", " + str(tileY))
                else:
                    tile.update_offset_position(self.position_offset, self.screen_data)
                    self.all_tile_sprites.add(tile.sprite)

                top_tile = self.top_tile_grid[tileX][tileY]
                if top_tile is not None:
                    top_tile.update_offset_position(self.position_offset, self.screen_data)
                    self.all_top_tile_sprites.add(top_tile.sprite)

    @staticmethod
    def load_tile_table(filename, width, height, use_transparency):
        if use_transparency:
            image = pygame.image.load(filename).convert_alpha()
        else:
            image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, int(image_width/width)):
            line = []
            tile_table.append(line)
            for tile_y in range(0, int(image_height/height)):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table
