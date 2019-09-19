import math
import sys
import random
from PIL import ImageFont
import level_handling
import pygame
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()


class Screen(object):
    # Screen object
    def __init__(self):
        self.title = "Fracture"
        self.screen_width = 800
        self.screen_height = 800
        self.top_padding = 200
        self.x_min = 50
        self.x_max = self.screen_width - self.x_min
        self.border_width = 20
        self.screen = self.set_screen()

    # Sets pygame window title display mode
    def set_screen(self):
        pygame.display.set_caption(self.title)
        size = (self.screen_width, self.screen_height)
        screen = pygame.display.set_mode(size)
        return screen


class Player(pygame.sprite.Sprite):
    # Player sprite
    def __init__(self, screen_obj):
        super().__init__()
        self.image = pygame.image.load("Media/player/player_default.png")
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = screen_obj.screen_width / 2 - self.size[1] / 2
        self.rect.y = screen_obj.screen_height - self.size[1] * 2
        self.speed = 7
        self.x_min = screen_obj.x_min
        self.x_max = screen_obj.x_max
        self.border_padding = screen_obj.border_width

    def get_segments(self, sphere):
        # Creates and returns a list of 4 segments by dividing the player
        # sprite's width by 4. Adds half the sphere image to the end of each
        # side for more realistic and accurate looking deflections.
        segments = []
        segment_width = self.size[0] / 4
        sphere_offset = sphere.size[0] / 2
        player_x = self.rect.x
        # Add the start and end x-axis px location for each segment to the list
        for i in range(4):
            if i == 0:  # Left segment of the player
                x_start = player_x - sphere_offset
                x_end = player_x + segment_width
            elif i == 3:  # Right segment of the player
                x_start = player_x
                x_end = x_start + segment_width + sphere_offset
            else:  # Middle two segments of the player
                x_start = player_x
                x_end = x_start + segment_width
            segments.append((x_start, x_end))
            player_x += segment_width
        return segments

    def move_left(self):
        # Handles moving the player to the left
        x = self.rect.x - self.speed - self.border_padding
        if x > self.x_min:
            self.rect.x -= self.speed
        return

    def move_right(self):
        # Handles moving the player to the right
        x = self.rect.x + self.size[0] + self.speed + self.border_padding
        if x < self.x_max:
            self.rect.x += self.speed
        return

    def update(self):
        # Overrides pygame's sprite.update function and handles player movement
        # Mouse
        if pygame.mouse.get_pressed()[0]:
            pygame.mouse.set_visible(False)
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < self.rect.x + self.size[0] / 2:
                self.move_left()
            if mouse_pos[0] > self.rect.x + self.size[0] / 2:
                self.move_right()
        # Left/Right arrow keys
        else:
            pygame.mouse.set_visible(True)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.move_left()
            if keys[pygame.K_RIGHT]:
                self.move_right()
        return


class Sphere(pygame.sprite.Sprite):
    def __init__(self, screen_obj):
        super().__init__()
        self.images = [
            pygame.image.load("Media/spheres/dark_blue.png")
            ]
        self.image = self.images[0]
        self.speed = 5
        self.speed_x = self.speed
        self.speed_y = self.speed * -1
        self.angle = 45
        self.player_angles = [300, 340, 20, 60]
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = screen_obj.screen_width / 2 - self.size[0] / 2
        self.rect.y = screen_obj.screen_height - self.size[1] * 10
        self.x_min = screen_obj.x_min + screen_obj.border_width
        self.x_max = screen_obj.screen_width - screen_obj.x_max - self.size[0]
        self.y_max = screen_obj.top_padding + screen_obj.border_width + self.size[1]
        self.px_locations = ("left", "right", "top", "bot", "top_left",
                             "top_right", "bot_left", "bot_right")

    def get_px_positions(self):
        # Creates and returns a list of the 8 pixels on the rectangle
        # surrounding the sphere: the 4 corners and the central point
        # on each side. The list will always be in the following order:
        # left, right, top, bot, top_left, top_right, bot_left, bot_right
        px_positions = [
            (self.rect.x, self.rect.y + self.size[1] / 2),
            (self.rect.x + self.size[0], self.rect.y + self.size[1] / 2),
            (self.rect.x + self.size[0] / 2, self.rect.y + self.size[1]),
            (self.rect.x + self.size[0] / 2, self.rect.y),
            (self.rect.x, self.rect.y),
            (self.rect.x + self.size[0], self.rect.y),
            (self.rect.x, self.rect.y + self.size[1]),
            (self.rect.x + self.size[0], self.rect.y + self.size[1])
        ]
        return px_positions

    def get_block_side_collision(self, block):
        # Returns the string representation of which of the sphere's 8 pixels
        # collided with the block. This is determined by comparing each pixel's
        # location against the coordinates of the block's sides and finding
        # which one lies within the block's boundaries.
        #
        # Loop through each of the (x,y) coords of the sphere's rect pixels and
        # check the x against the block's left and right sides, then y against
        # the top and bottom. If both are true, it lies within the block. The
        # sides are always in the following order: left, right, top, bottom.
        block_sides = block.get_sides()
        index = 0
        for position in self.get_px_positions():
            if block_sides[0] <= position[0] <= block_sides[1]:
                if block_sides[2] <= position[1] <= block_sides[3]:
                    break
            index += 1
        return self.px_locations[index]

    def set_block_deflection_angle(self, block):
        # Calculates the sphere's new angle based on the side of the block hit.
        block_side = self.get_block_side_collision(block)
        print(block_side)
        if block_side == "left" or block_side == "right":
            self.angle = 360 - self.angle
        elif block_side == "top" or block_side == "bot":
            self.angle = (180 - self.angle) % 360
        else:
            angle = self.angle - 360
            if angle < 0:
                angle = 360 - angle
            self.angle = angle
        return

    def set_border_deflection_angle(self, border):
        # Calculates the sphere's new angle based on the border hit.
        if border.side == "left":
            self.angle = 360 - self.angle
        if border.side == "right":
            self.angle = 360 - self.angle
        if border.side == "top":
            self.angle = (180 - self.angle) % 360

        # Place holder for sphere/bottom border collision handling
        if border.side == "bot":
            pass
        return

    def set_player_deflection_angle(self, player_segments):
        # Calculates the sphere's new angle based on the player segment hit.
        # Sphere's bottom center x pixel coord
        sphere_x = self.rect.x + self.size[0] / 2
        segment_num = 0
        for start, end in player_segments:
            if start <= sphere_x <= end:
                break
            segment_num += 1
        # Ensure the segment number is not greater than the angles list length
        if segment_num < len(self.player_angles):
            self.angle = self.player_angles[segment_num]
        # If, for some reason, it is, then reverse the angle of the sphere
        else:
            self.angle = 360 - self.angle
        return

    def move(self):
        # Moves the sphere by converting the angle into radians and then using
        # sin and cos to calculate the x/y speeds, or number of pixels to move.
        radians = math.radians(self.angle)
        self.rect.y += int(self.speed_y * math.cos(radians))
        self.rect.x += int(self.speed_x * math.sin(radians))
        return

    def update(self, game):
        # Overrides pygame's sprite.update function and updates the sphere.
        # Checks for border, player, and block collisions, then handles movement.
        game.border_collision()
        game.player_collision()
        game.block_collision()
        self.move()
        return


class Game(object):
    # Primary game object class that handles the game's functionality.
    def __init__(self):
        self.screen_obj = Screen()
        self.sphere_sprites = pygame.sprite.RenderUpdates()
        self.border_sprites = pygame.sprite.RenderPlain()
        self.player_sprites = pygame.sprite.RenderUpdates()
        self.block_sprites = pygame.sprite.RenderPlain()
        self.all_sprites = pygame.sprite.Group()

        # Time Handling
        self.clock = pygame.time.Clock()
        self.max_FPS = 60
        self.frame_count = 0
        self.seconds = 0
        self.blink_frame_count = 0
        self.blink_delay = .5
        self.blinking = True

        # Prompts
        self.title_prompt = "PRESS ENTER"

        # Levels
        self.level_num = 1
        self.level_obj = level_handling.Level(self.level_num, self.screen_obj)

        # Fonts/Colors
        self.master_font = "Media/ariblk.ttf"
        self.font_size = 20
        self.text_color = (255, 255, 255)
        self.font = ImageFont.truetype(self.master_font, self.font_size)
        self.word_font = pygame.font.Font(self.master_font, self.font_size)

        # Media
        self.game_background = pygame.image.load("Media/backgrounds/space1.png")
        self.title_image = pygame.image.load("Media/title_image.png")

    #####################
    #    Game Control   #
    #####################
    def update_seconds(self):
        # Time handler for tracking the on/off of blinking text. Compares a
        # copy of the number of game frames against the max frames per second
        # and returns true if equal or false if not.
        self.blink_frame_count += 1
        blink_frame_count = self.max_FPS * self.blink_delay
        if self.blink_frame_count == blink_frame_count:
            self.blink_frame_count = 0
            return True
        return False

    def check_frame_count(self):
        # Tracks the number of seconds elapsed by comparing the frame count
        # against the max frames per second.
        if self.frame_count >= self.max_FPS:
            self.frame_count = 0
            self.seconds += 1
        return

    def continue_game(self, title_screen=False):
        # Primary game time handler. Checks if user has pressed enter on the
        # title screen to move on to the game screen or if the user has exited
        # the game by closing the window. Also handles ticking the game clock,
        # and tracking the frame count.
        if self.get_game_events(title_screen):
            return False
        self.clock.tick(self.max_FPS)
        self.frame_count += 1
        self.check_frame_count()
        return True

    def check_level_status(self):
        # Checks how many blocks remain. If none, the level is complete.
        # TODO add level completion.
        if len(self.block_sprites) == 0:
            print("winner")
        return

    def play(self):
        # Primary game loop function. Gets the initial game start sprite lists,
        # draws screen and sprite images, then updates the sprites and display.
        self.get_sprites()
        while self.continue_game():
            self.draw_game_background()
            self.all_sprites.draw(self.screen_obj.screen)
            self.draw_borders()
            self.player_sprites.update()
            self.sphere_sprites.update(self)
            self.check_level_status()
            pygame.display.update()

            # TODO
            # # If player has advanced to next level, get appropriate level
            # if self.level_obj.check_level(self.level_num):
            #     self.level_obj = Level(self.level_num)
        return

    @staticmethod
    def quit_game():
        # Handles the game closing, quits pygame and exits the program.
        pygame.quit()
        sys.exit(0)

    #####################
    #      Getters      #
    #####################
    @staticmethod
    def get_game_events(title_screen=False):
        # Gets pygame events and returns true/false if the user quit the game
        # by closing the game window. Also returns true/false if on the title
        # screen and the player presses enter.

        # mouse_position = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return True
            if title_screen:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True
        return False

    def get_border_sprites(self):
        # Creates the left, right, top, and bottom border sprites.
        self.border_sprites.add(level_handling.Border(self.screen_obj, "left"))
        self.border_sprites.add(level_handling.Border(self.screen_obj, "right"))
        self.border_sprites.add(level_handling.Border(self.screen_obj, "top"))
        self.border_sprites.add(level_handling.Border(self.screen_obj, "bot"))
        return

    def get_block_sprites(self):
        # Converts the current level's block list into sprites.
        for block in self.level_obj.blocks:
            self.block_sprites.add(level_handling.Block(block))
        return

    def get_all_sprites(self):
        # Adds all sprite groups to a primary group.
        for border in self.border_sprites:
            self.all_sprites.add(border)
        for sphere in self.sphere_sprites:
            self.all_sprites.add(sphere)
        for player in self.player_sprites:
            self.all_sprites.add(player)
        for block in self.block_sprites:
            self.all_sprites.add(block)
        return

    def get_sprites(self):
        # Handles creation of all the sprite groups.
        self.get_border_sprites()
        self.sphere_sprites.add(Sphere(self.screen_obj))
        self.player_sprites.add(Player(self.screen_obj))
        self.get_block_sprites()
        self.get_all_sprites()
        return

    def get_sphere_border_collision(self, sphere):
        # Returns result of pygame's sprite collision function call between
        # the sphere and the border sprite group.
        border_collision = pygame.sprite.spritecollide(
            sphere,
            self.border_sprites,
            False
        )
        return border_collision

    def get_sphere_block_collision(self, sphere):
        # Returns result of pygame's sprite collision function call between
        # the sphere and the block sprite group.
        block_collision = pygame.sprite.spritecollide(
            sphere,
            self.block_sprites,
            False
        )
        return block_collision

    def get_sphere_player_collision(self):
        # Returns result of pygame's sprite collision function call between
        # the sphere sprite group and the player sprite group.
        collisions = pygame.sprite.groupcollide(
            self.sphere_sprites,
            self.player_sprites,
            0,
            0
        )
        return collisions

    #####################
    #     Collision     #
    #####################
    def border_collision(self):
        for sphere in self.sphere_sprites:
            border_collision = self.get_sphere_border_collision(sphere)
            if border_collision:
                border = border_collision[0]
                if border.side == "bot":
                    sphere.kill()
                    continue
                sphere.set_border_deflection_angle(border)
        return

    def block_collision(self):
        # Iterates through each sphere in the sphere sprite group and checks
        # for block collision. The block's image is updated or killed depending
        # on the block's health.
        for sphere in self.sphere_sprites:
            block_collision = self.get_sphere_block_collision(sphere)
            if block_collision:
                block = block_collision[0]
                sphere.set_block_deflection_angle(block)

                # TODO change block image dependent on health, add unbreakable
                # blocks, scoring, etc.
                if block.health == 1:
                    block.kill()
                else:
                    block.health -= 1
        return

    def player_collision(self):
        # Handles sphere/player collisions. Gets dictionary of player and
        # sphere collisions and sets the angle of the sphere based on which
        # player segment was hit.
        player_collision = self.get_sphere_player_collision()
        for sphere in player_collision:
            player = player_collision[sphere][0]
            segments = player.get_segments(sphere)
            sphere.set_player_deflection_angle(segments)
        return

    #####################
    #      Drawing      #
    #####################
    def draw_borders(self):
        for border in self.border_sprites:
            border.draw(self.screen_obj)
        return

    def draw_game_background(self):
        # self.screen_obj.screen.blit(self.game_background, (0, 0))
        self.screen_obj.screen.fill((0, 0, 0))
        return

    #####################
    #    Title Screen   #
    #####################
    def blink_text(self):
        # Handles blinking title screen text.
        if self.update_seconds():
            if self.blinking:
                self.blinking = False
                return True
            else:
                self.blinking = True
        if self.blinking:
            self.draw_blink_text(self.title_prompt)
        return False

    def draw_blink_text(self, prompt):
        # Draws the title screen blink text.
        text = self.word_font.render(prompt, 1, self.text_color)
        size = self.font.getsize(prompt)
        x = self.screen_obj.screen_width / 2 - size[0] / 2
        y = self.screen_obj.screen_height / 2 + size[1]
        self.screen_obj.screen.blit(text, (x, y))
        return

    def draw_title_image(self):
        # Draws the title screen game text.
        size = self.title_image.get_size()
        x = self.screen_obj.screen_width / 2 - size[0] / 2
        y = size[1]
        self.screen_obj.screen.blit(self.title_image, (x, y))
        return

    def title_screen(self):
        # Handles the game's title screen.
        while self.continue_game(True):
            self.draw_game_background()
            self.draw_title_image()
            self.blink_text()
            pygame.display.update()
        return


#####################
#        Main       #
#####################
def main():
    # Primary application loop. Initializes the game object, runs the title
    # screen, plays the game, and quits.
    game = Game()
    game.title_screen()
    game.play()
    game.quit_game()


if __name__ == "__main__":
    main()
