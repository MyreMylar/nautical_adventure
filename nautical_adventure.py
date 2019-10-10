import pygame
import random
from pygame.locals import *

from map_editor import MapEditor
from game.main_menu import MainMenu
from game.player import Player

from game.ai_spawner import AISpawner
from game.player_health_bar import HealthBar
from game.player_cannon_ui import CannonUI
from game.tiled_level import TiledLevel
from game.pick_up import PickUpSpawner

from game.wind import Wind
from game.wind_gauge import WindGauge

from game.trade_good import TradeGood
        

class ScreenData:
    def __init__(self, hud_size, editor_hud_size, screen_size):
        self.screen_size = screen_size
        self.hud_dimensions = hud_size
        self.editor_hud_dimensions = editor_hud_size
        self.play_area = [self.screen_size[0], self.screen_size[1] - self.hud_dimensions[1]]

    def set_editor_active(self):
        self.play_area = [self.screen_size[0], self.screen_size[1] - self.editor_hud_dimensions[1]]


def main():
    pygame.init()
    pygame.key.set_repeat()
    x_screen_size = 1024
    y_screen_size = 600
    screen_data = ScreenData([x_screen_size, 152], [x_screen_size, 184], [x_screen_size, y_screen_size])
    screen = pygame.display.set_mode(screen_data.screen_size)
    pygame.display.set_caption('Nautical Adventure')
    background = pygame.Surface(screen.get_size())
    background = background.convert(screen) 
    background.fill((95, 140, 95))

    player_sprites = pygame.sprite.OrderedUpdates()
    all_tile_sprites = pygame.sprite.Group()
    all_top_tile_sprites = pygame.sprite.Group()
    all_monster_sprites = pygame.sprite.OrderedUpdates()
    all_pick_up_sprites = pygame.sprite.Group()
    all_explosion_sprites = pygame.sprite.Group()
    all_projectile_sprites = pygame.sprite.Group()
    ui_sprite_group = pygame.sprite.Group()

    fonts = []
    small_font = pygame.font.Font(None, 16)
    font = pygame.font.Font(None, 32)
    large_font = pygame.font.Font(None, 64)

    fonts.append(small_font)
    fonts.append(font)
    fonts.append(large_font)

    wind = Wind(-14, 14)
    wind_gauge = WindGauge([x_screen_size/2, y_screen_size - 76], wind.min, wind.max, small_font)

    all_tradeable_goods = [TradeGood("Banana", [5, 7]), TradeGood("Tobacco", [10, 15]),
                           TradeGood("Timber", [1, 3]), TradeGood("Sugar", [8, 12]),
                           TradeGood("Coffee", [10, 12]), TradeGood("Furs", [7, 9]),
                           TradeGood("Spices", [20, 30]), TradeGood("Gems", [50, 75])]
    tiled_level = TiledLevel([64, 64], all_tile_sprites, all_top_tile_sprites,
                             screen_data, all_tradeable_goods)
    tiled_level.load_tiles()
    main_menu = MainMenu(fonts)
    
    explosions_sprite_sheet = pygame.image.load("images/explosions.png").convert_alpha()

    all_ui_windows = []
    players = []
    monsters = []
    pick_ups = []
    projectiles = []
    explosions = []
    new_explosions = []
    hud_buttons = []
    player = None

    hud_rect = pygame.Rect(0, screen_data.screen_size[1] - screen_data.hud_dimensions[1],
                           screen_data.hud_dimensions[0], screen_data.hud_dimensions[1])

    editor_hud_rect = pygame.Rect(0, screen_data.screen_size[1] - screen_data.editor_hud_dimensions[1],
                                  screen_data.editor_hud_dimensions[0], screen_data.editor_hud_dimensions[1])

    editor = MapEditor(tiled_level, editor_hud_rect, fonts)

    health_bar = HealthBar([screen_data.hud_dimensions[0] - (screen_data.hud_dimensions[0] * 0.20),
                            screen_data.screen_size[1] - (0.6 * screen_data.hud_dimensions[1])],
                           (screen_data.hud_dimensions[0] * 0.15), 16, small_font)
    cannon_ui = CannonUI([screen_data.hud_dimensions[0] * 0.08,
                          screen_data.screen_size[1] - (0.9 * screen_data.hud_dimensions[1])],
                         (screen_data.hud_dimensions[0] * 0.15), 16, small_font)
    pick_up_spawner = PickUpSpawner(pick_ups, all_pick_up_sprites)
    ai_spawner = AISpawner(monsters, all_monster_sprites, tiled_level)
    clock = pygame.time.Clock()        
    running = True
    
    is_main_menu = True
    is_editor = False
        
    is_game_over = False
    restart_game = False
    win_message = ""

    new_highscore = 0
    has_new_high_score = False

    while running:
        frame_time = clock.tick()
        time_delta = frame_time/1000.0

        if is_main_menu:
            is_main_menu_and_index = main_menu.run(screen, screen_data)
            if is_main_menu_and_index[0] == 0:
                is_main_menu = True
            elif is_main_menu_and_index[0] == 1:
                is_main_menu = False
            elif is_main_menu_and_index[0] == 2:
                is_main_menu = False
                is_editor = True
            if not is_main_menu:
                player = Player(tiled_level, tiled_level.find_player_start(),
                                explosions_sprite_sheet, hud_buttons, all_tradeable_goods)
                players.append(player)

                for tile in tiled_level.walkable_tiles:
                    chance_of_flotsam = random.randint(1, 250)
                    if chance_of_flotsam == 1:
                        pick_up_spawner.try_spawn(tile.world_position)
                        
        elif is_editor:
            screen_data.set_editor_active()
            running = editor.run(screen, background, all_tile_sprites,
                                 all_top_tile_sprites, editor_hud_rect, time_delta)
                  
        else:
 
            if restart_game:
                restart_game = False

                new_highscore = 0

                # clear all stuff
                players[:] = []
                monsters[:] = []
                projectiles[:] = []
                explosions[:] = []
                new_explosions[:] = []
                all_monster_sprites.empty()

                is_game_over = False
                # recreate
                ai_spawner = AISpawner(monsters, all_monster_sprites, tiled_level)
                player = Player(tiled_level, tiled_level.find_player_start(),
                                explosions_sprite_sheet, hud_buttons, all_tradeable_goods)
                players.append(player)
                  
            elif is_game_over:
                pass
            else:
                pass

            if player.health <= 0:
                is_game_over = True
                win_message = "You have been sunk!"
                
            wind.update(time_delta)
            wind_gauge.update_wind_direction_and_strength(wind)
             
            all_projectile_sprites.empty()
            all_explosion_sprites.empty()
            player_sprites.empty()
            all_monster_sprites.empty()
                   
            # handle UI and inout events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if is_game_over:
                    if event.type == KEYDOWN:
                        if event.key == K_y:
                            restart_game = True
                for player in players:
                    player.process_event(event)

            ai_spawner.update()
            health_bar.update(player.health, player.max_health)
            cannon_ui.update(player.reload_counter, player.reload_time)

            tiled_level.update_offset_position(player.position,
                                               all_tile_sprites,
                                               all_top_tile_sprites)
            
            for pick_up in pick_ups:
                pick_up.update_movement_and_collision(player, tiled_level)
            pick_ups[:] = [pick_up for pick_up in pick_ups if not pick_up.should_die]

            for player in players:
                player.update_movement_and_collision(time_delta, projectiles, tiled_level,
                                                     monsters, all_ui_windows, ui_sprite_group, fonts, wind)
                player_sprites = player.update_sprite(player_sprites, time_delta)
                if player.should_die and player.has_new_high_score:
                    new_highscore = player.score
                    has_new_high_score = True
                
            players[:] = [player for player in players if not player.should_die]

            for monster in monsters:
                monster.update_movement_and_collision(time_delta, player,
                                                      new_explosions, tiled_level.collidable_tiles,
                                                      monsters, pick_up_spawner, wind, projectiles)
                monster.update_sprite(all_monster_sprites, time_delta)
            monsters[:] = [monster for monster in monsters if not monster.should_die]
            new_explosions[:] = []

            for projectile in projectiles:
                projectile.update_movement_and_collision(tiled_level.collidable_tiles, player,
                                                         monsters, time_delta, tiled_level, new_explosions, explosions)
                all_projectile_sprites = projectile.update_sprite(all_projectile_sprites)
            projectiles[:] = [projectile for projectile in projectiles if not projectile.should_die]

            for explosion in explosions:
                all_explosion_sprites = explosion.update_sprite(all_explosion_sprites, time_delta)
            explosions[:] = [explosion for explosion in explosions if not explosion.should_die]
            
            screen.blit(background, (0, 0))  # draw the background

            all_tile_sprites.draw(screen)
            all_pick_up_sprites.draw(screen)
            all_monster_sprites.draw(screen)
            player_sprites.draw(screen)
            all_explosion_sprites.draw(screen)
            all_projectile_sprites.draw(screen)
         
            pygame.draw.rect(screen, pygame.Color(60, 60, 60), hud_rect, 0)  # draw the hud
            health_bar.draw(screen)
            cannon_ui.draw(screen)
            wind_gauge.draw(screen)

            for window in all_ui_windows:
                window.update()
                window.draw(screen)

            ui_sprite_group.update()
            ui_sprite_group.draw(screen)

            player_gold_hud_text = small_font.render("Gold: " + str(player.gold), True, pygame.Color(255, 255, 255))
            screen.blit(player_gold_hud_text,
                        player_gold_hud_text.get_rect(x=screen_data.hud_dimensions[0] * 0.755,
                                                      centery=screen_data.screen_size[1] * 0.78))

            cargo_str = "Cargo space: " + str(player.space_in_hold) + "/" + str(player.hold_size)
            cargo_space_text = small_font.render(cargo_str,
                                                 True, pygame.Color(255, 255, 255))
            screen.blit(cargo_space_text,
                        cargo_space_text.get_rect(x=screen_data.hud_dimensions[0] * 0.755,
                                                  centery=screen_data.screen_size[1] * 0.82))

            if not player.should_die:
                for button in hud_buttons:
                    if button.button_image_name == "rifle_icon":
                        button.update_text_values(player.rifle_weapon.ammo_count)
                    elif button.button_image_name == "shotgun_icon":
                        button.update_text_values(player.shotgun_weapon.ammo_count)
                    elif button.button_image_name == "launcher_icon":
                        button.update_text_values(player.launcher_weapon.ammo_count)
                    button.draw_text(screen)
                                   
            if is_game_over:
                win_message_text_render = large_font.render(win_message,
                                                            True, pygame.Color(255, 255, 255))
                win_message_text_render_rect = win_message_text_render.get_rect(centerx=x_screen_size/2,
                                                                                centery=(y_screen_size/2)-128)

                if has_new_high_score:
                    high_score_text_render = font.render("New Highscore: " + str(new_highscore),
                                                         True, pygame.Color(255, 200, 150))
                    high_score_text_render_rect = high_score_text_render.get_rect(centerx=x_screen_size/2,
                                                                                  centery=(y_screen_size/2)-90)
                    screen.blit(high_score_text_render, high_score_text_render_rect)

                play_again_text_render = font.render("Play Again? Press 'Y' to restart", True,
                                                     pygame.Color(255, 255, 255))
                play_again_text_render_rect = play_again_text_render.get_rect(centerx=x_screen_size/2,
                                                                              centery=(y_screen_size/2)-40)
                screen.blit(win_message_text_render, win_message_text_render_rect)
                
                screen.blit(play_again_text_render, play_again_text_render_rect)

        pygame.display.flip()  # flip all our drawn stuff onto the screen

    pygame.quit()  # exited game loop so quit pygame


if __name__ == '__main__':
    main()
