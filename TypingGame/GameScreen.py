import pygame
import random


#####################
#      Getters      #
##################### 
def get_words_per_min(game):
    one_min = 60
    gwpm = str(game.gross_words_per_min)
    average_chars = game.characters_typed / game.avg_word_length
    average_time = game.seconds / one_min
    gwpm = round(average_chars / average_time)
    return gwpm

def get_gwpm_text_size(game):
    gwpm = str(game.gross_words_per_min)
    text_string = game.gwpm_prompt + str(gwpm)
    text_size = game.font.getsize(text_string)
    text = game.word_font.render(text_string, 1, game.text_color)
    return text, text_size[0]

def get_stopwatch_string(game):
    game_seconds = game.seconds
    seconds = game_seconds % 60
    mins = game_seconds // 60
    hours = game_seconds // 60 // 60
    if (hours > 0):
        stopwatch = (f"{hours:02}:{mins:02}:{seconds:02}")
    elif (mins > 0):
        stopwatch = (f"{mins:02}:{seconds:02}")
    else:
        stopwatch = (f"{seconds:02}")
    return stopwatch

def get_stopwatch_location(game, text_size):
    char_size = game.font.getsize("0")
    bubble_size = game.right_corner.get_size()
    x = 0 + (bubble_size[0] * game.right_corner_x_offset) / 2
    x -= text_size[0] / 2 + char_size[0]
    y = game.screenH - game.bottom_boxH * 2
    return x, y

def get_score_multiplier_location(text_size, game):
    char_size = game.font.getsize("0")
    image_size = game.right_corner.get_size()
    x = game.screenW - (image_size[0] * game.right_corner_x_offset) / 2
    x -= text_size[0] / 2 - char_size[0]
    y = game.screenH - game.bottom_boxH * 2
    return x, y
#####################
#   Word Handling   #
#####################   
def remove_words_from_screen(screen, game):
    if (game.player_input):
        player_input = game.player_input.split(' ')
        for word in reversed(game.current_words):
            for player_word in player_input:
                if (player_word == word.word):
                    game.player_score += len(word.word) * game.word_delay_score_multiplier
                    game.characters_typed += len(word.word) + 1
                    try:
                        game.current_words.remove(word)   # TODO fix (list.remove(x): x not in list) exception
                    except:
                        continue
                    game.add_word_bubble(word, screen)
                    game.button_hover_sound.play()
    return

def check_word_count(game):
    if (len(game.current_words) < game.add_words_trigger):
        #words_to_add = game.add_words_trigger - 1
        #for i in range(words_to_add):
        game.current_words.append(random.choice(game.wordbank))
    return

def word_str_to_obj(game):
    new_words = []
    for word in game.current_words:
        if (type(word) is str):
            new_words.append(game.get_word_object(word))
        else:
            new_words.append(word)
    game.current_words = new_words
    return

def add_word(game):
    new_word = random.choice(game.wordbank)
    game.current_words.append(new_word)
    return

def word_fail(word, screen, game):
    game.player_score -= len(word.word) #* game.score_multiplier
    game.current_words.remove(word)
    game.add_word_bubble(word, screen)
    game.button_hover_sound.play()
    return

def move_word_up(word, screen, game):
    position = word.y + word.speed
    if (position > 0):
        word.y += word.speed
    else:
        word_fail(word, screen, game)
    return

def move_word_down(word, screen, game):
    position = word.y - word.speed
    text_height = game.get_score_text_size(word.word, "height")
    input_box_height = game.bottom_boxH - game.border_width * 2
    height = game.screenH - text_height - input_box_height - game.font_size / 2
    if (position < height):
        word.y += word.speed
    else:
        word_fail(word, screen, game)
    return

def move_words(screen, game):
    for word in game.current_words:
        try:
            if (game.up_or_down == -1):
                move_word_up(word, screen, game)
            else:
                move_word_down(word, screen, game)
        except AttributeError:
            break
    return


#####################
#   Event Handling  #
#####################
def start_game(button, game):
    game.words_moving = True
    button.visible = True
    return

def toggle_pause(game):
    if (game.words_moving):
        game.words_moving = False
    else:
        game.words_moving = True
    return

def toggle_mute(game):
    if (game.music_playing):
        pygame.mixer.music.pause()
        game.music_playing = False
    else:
        pygame.mixer.music.unpause()
        game.music_playing = True
    return

def update_player_input(events, game):
    if (game.words_moving):
        if (game.player_input_obj.update(events, game)):
            game.player_input = game.player_input_obj.get_text()
            game.player_input_obj.reset_input_text()
    return

def check_buttons(game, button):
    if (button.text == "Start"):
        start_game(button, game)
    elif (button.text == "Pause"):
        toggle_pause(game)
    elif (button.text == "Mute"):
        toggle_mute(game)
    elif (button.text == "+"):
        game.set_game_speed_up()
    elif (button.text == "-"):
        game.set_game_speed_down()
    return

def check_mouse_position(mouse_position, buttons, game):
    for button in buttons:
        if (button.is_over(mouse_position)):
            button.color = game.button_hover_color
            button.text_color = game.button_text_color
            button.hovering = True
            if (button.play_sound):
                game.button_hover_sound.play()
                button.play_sound = False
        else:
            button.color = game.button_color
            button.text_color = game.button_text_color
            button.hovering = False
            button.play_sound = True
    return

def check_button_clicked(mouse_position, buttons, game):
    for button in buttons:
        if (button.is_over(mouse_position)):
            check_buttons(game, button)
    return

def check_events(game, buttons):
    mouse_position = pygame.mouse.get_pos()
    events = pygame.event.get()
    for event in events:
        if (event.type == pygame.QUIT):
            game.quit_game()      
        elif (event.type == pygame.KEYDOWN):
            pass
        elif (event.type == pygame.MOUSEMOTION):
            check_mouse_position(mouse_position, buttons, game)
        elif (event.type == pygame.MOUSEBUTTONDOWN):
            check_button_clicked(mouse_position, buttons, game)
    update_player_input(events, game)
        # TODO add functionality to return false and break the loop
    return True

def continue_game(screen, game):
    check_word_count(game)
    if (game.add_word_delay < 1):
        if (game.check_quick_frame_count()):
            add_word(game)
    elif (game.add_word_seconds >= game.add_word_delay):
        game.quick_frame_count = 0
        add_word(game)
        game.add_word_seconds = 0
    word_str_to_obj(game)
    remove_words_from_screen(screen, game)
    move_words(screen, game)
    game.pop_word_bubbles(screen)
    pygame.display.update()
    return

#####################
#      Drawing      #
#####################
def draw_input_text(screen, game):
    player_input = game.player_input_obj.get_surface()
    size = game.player_input_obj.input_size
    x = game.screenW / 2 - size[0] / 2
    y = game.get_bottom_offset(game.score_prompt) + game.border_width
    screen.blit(player_input, (x,y))
    return

def draw_elapsed_time(screen, game):
    text_string = get_stopwatch_string(game)
    text_size = game.font.getsize(text_string)
    text = game.word_font.render(text_string, 1, game.text_color)
    x, y = get_stopwatch_location(game, text_size)
    screen.blit(text, (x,y))
    return

def draw_words_per_min(screen, game):
    if (game.characters_typed != 0 and game.seconds != 0):
        gwpm = get_words_per_min(game)
        game.gross_words_per_min = gwpm
    text, text_width = get_gwpm_text_size(game)
    x = 0 + game.input_left_padding
    y = game.get_bottom_offset(game.player_score)
    screen.blit(text, (x,y))
    draw_elapsed_time(screen, game)
    return

def draw_score_multiplier(screen, game):
    score_mult = game.word_delay_score_multiplier # TODO add functionality for correct words in a row
    text_string = "x " + str(score_mult)
    text = game.word_font.render(text_string, 1, game.text_color)
    text_size = game.font.getsize(text_string)
    x, y = get_score_multiplier_location(text_size, game)
    screen.blit(text, (x,y))
    return

def draw_score_text(screen, game):
    text_string = game.score_prompt + str(game.player_score)
    text = game.word_font.render(text_string, 1, game.text_color)
    right_offset = game.get_right_offset(game.player_score)
    x = right_offset + game.buttonW
    y = game.get_bottom_offset(game.player_score)
    screen.blit(text, (x,y))
    draw_score_multiplier(screen, game)
    return

def draw_input_top(screen, game):
    image_size = game.right_corner.get_size()
    x_start = 0 + image_size[0] * .75
    x_end = game.screenW - image_size[0] * .75
    game.input_width = x_end - x_start
    y = game.screenH - game.bottom_boxH
    pygame.draw.line(screen, game.text_color, (x_start,y), (x_end,y), game.border_width)
    return

def draw_corner_bubble(screen, game, left_bubble=False):
    image_size = game.right_corner.get_size()
    y = game.screenH - image_size[1] * game.bubble_y_offset
    if (left_bubble):
        x = 0 - image_size[0] * game.left_corner_x_offset
        screen.blit(game.left_corner, (x,y))
    else:
        x = game.screenW - image_size[0] * game.right_corner_x_offset
        screen.blit(game.right_corner, (x,y))
    return

def draw_left_game_menu_bubble(screen, game):
    image_size = game.game_menu_top_left.get_size()
    y = game.screenH - game.bottom_boxH - image_size[1]
    image_size = game.right_corner.get_size()
    x = 0 + image_size[0] * .75
    screen.blit(game.game_menu_top_left, (x, y))
    return

def draw_right_game_menu_bubble(screen, game):
    image_size = game.game_menu_top_right.get_size()
    y = game.screenH - game.bottom_boxH - image_size[1]
    x = game.screenW - image_size[0]
    image_size = game.right_corner.get_size()
    x -= image_size[0] * game.right_corner_x_offset
    screen.blit(game.game_menu_top_right, (x, y))
    return

def draw_game_menu_bubbles(screen, game):
    draw_left_game_menu_bubble(screen, game)
    draw_right_game_menu_bubble(screen, game)
    return

def draw_hud(screen, game):
    draw_corner_bubble(screen, game)
    draw_corner_bubble(screen, game, True)
    draw_input_top(screen, game)
    draw_game_menu_bubbles(screen, game)
    return

def draw_bubble(button, screen, game): # TODO refractor
    if (button.text == "Pause" or button.text == "Mute"):
        image_size = game.game_button_left.get_size()
        x = button.x - image_size[0] * game.left_corner_x_offset
        text_size = game.font.getsize(button.text)
        y = button.y - (image_size[1] - text_size[1]) / 2 + text_size[1] / 2
        screen.blit(game.game_button_left, (x,y))
    elif (button.text == "Speed"):
        image_size = game.game_button_right.get_size()
        x = game.screenW - image_size[0] * game.right_corner_x_offset
        y =  game.screenH / 2 - image_size[1] / 2
        screen.blit(game.game_button_right, (x,y))
    elif (button.text == "+"):
        pixel_offset = 24
        image_size = game.speed_change.get_size()
        speed_bubble_size = game.speed_image.get_size()
        text_size = game.font.getsize(button.text)
        x = button.x - text_size[0] - pixel_offset
        text_size = game.font.getsize("Speed")
        y =  game.screenH / 2 - image_size[1] - speed_bubble_size[1] - 20
        screen.blit(game.speed_change, (x,y))
    elif (button.text == "-"):
        pixel_offset = 30
        speed_bubble_size = game.speed_image.get_size()
        text_size = game.font.getsize(button.text)
        x = button.x - text_size[0] - pixel_offset
        text_size = game.font.getsize("Speed")
        y = button.y - speed_bubble_size[1] + text_size[1] / 2 + 5
        screen.blit(game.speed_change, (x,y))
    return


# TODO update images
def draw_button_bubbles(buttons, screen, game):
    for button in buttons:
        #if (button.text == "Pause"):
        #    screen.blit(game.pause_image, (button.x, button.y))
        #    draw_bubble(button, screen, game)
        if (button.text == "Pause"):
            screen.blit(game.pause_image, (button.x, button.y))
            draw_bubble(button, screen, game)
        elif (button.text == "Mute"):
            screen.blit(game.mute_image, (button.x, button.y))
            draw_bubble(button, screen, game)
        elif (button.text == "Speed"):
            screen.blit(game.speed_image, (button.x, button.y))
            draw_bubble(button, screen, game)
        elif (button.text == "+"):
            screen.blit(game.speed_up, (button.x, button.y))
            draw_bubble(button, screen, game)
        elif (button.text == "-"):
            screen.blit(game.speed_down, (button.x, button.y))
            draw_bubble(button, screen, game)




        elif (button.text == "Test"):
            screen.blit(game.test, (button.x, button.y))
            draw_bubble(button, screen, game)


    return

def draw_words(screen, game):
    for word in game.current_words:
        text = game.word_font.render(word.word, 1, word.text_color)
        screen.blit(text, (word.x, word.y))
    return

def draw_game_screen(screen, game, buttons):
    game.draw_bg_image(screen)
    draw_words(screen, game)
    draw_button_bubbles(buttons, screen, game)
    draw_hud(screen, game)
    draw_score_text(screen, game)
    draw_words_per_min(screen, game)
    draw_input_text(screen, game)
    game.draw_buttons(screen)
    pygame.display.update()
    return


#####################
#    Game Screen    #
#####################
def play(screen, game):
    game.play_music(game.game_music)
    buttons = game.get_game_buttons()
    game.seconds = 0
    while(True):
        game.clock.tick(game.max_FPS)
        game.frame_count += 1
        if not (check_events(game, buttons)):
            break
        if (game.words_moving):
            continue_game(screen, game)
            game.check_frame_count()
        draw_game_screen(screen, game, buttons)
    game.reset_buttons()
    return