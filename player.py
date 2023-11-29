import pygame
from otherEntities import Cat, Ladder

# Screen dimensions
WIDTH, HEIGHT = 1280, 720

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)

# Load player spritesheet
player_spritesheet = pygame.image.load("player.png")

# Extracting stationary sprite from the player sprite sheet
stationary_sprite = pygame.Surface((16, 16), pygame.SRCALPHA)
stationary_sprite.blit(player_spritesheet, (0, 0), (16, 16, 16, 16))
stationary_sprite = pygame.transform.scale(stationary_sprite, (64, 64))


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.velocity_x = 5
        self.velocity_y = 0
        self.base_velocity_x = -5
        self.jump_force = 25
        self.is_jumping = False
        self.stationary_sprite = stationary_sprite  # Store the stationary sprite
        self.running_right_sprites = [
            pygame.transform.scale(player_spritesheet.subsurface((16, 32, 16, 16)), (64, 64)),  # Sprite 1
            pygame.transform.scale(player_spritesheet.subsurface((32, 32, 16, 16)), (64, 64)),  # Sprite 2
            pygame.transform.scale(player_spritesheet.subsurface((48, 32, 16, 16)), (64, 64))  # Sprite 3
        ]
        self.running_left_sprites = [
            pygame.transform.flip(self.running_right_sprites[0], True, False),  # Flip Sprite 1
            pygame.transform.flip(self.running_right_sprites[1], True, False),  # Flip Sprite 2
            pygame.transform.flip(self.running_right_sprites[2], True, False)  # Flip Sprite 3
        ]
        self.current_sprite_index = 0  # Index to keep track of the current sprite
        self.sprite = self.stationary_sprite  # Set the sprite initially to stationary_sprite
        self.facing_right = True  # Keep track of the direction the player is facing
        self.sprite_update_counter = 0  # Initialize a sprite update counter
        self.sprite_update_frequency = 5  # Set the update frequency

        self.stationary_sprites = [
            pygame.transform.scale(player_spritesheet.subsurface((16, 16, 16, 16)), (64, 64)),  # Sprite 1
            pygame.transform.scale(player_spritesheet.subsurface((32, 16, 16, 16)), (64, 64)),  # Sprite 2
            pygame.transform.scale(player_spritesheet.subsurface((48, 16, 16, 16)), (64, 64))  # Sprite 3
        ]
        self.current_stationary_sprite_index = 0  # Index to keep track of the current stationary sprite
        self.stationary_sprite = self.stationary_sprites[self.current_stationary_sprite_index]
        self.stationary_sprite_update_counter = 0  # Initialize a stationary sprite update counter
        self.stationary_sprite_update_frequency = 5  # Set the update frequency

        self.is_dead = False
        self.death_sprite = pygame.transform.scale(player_spritesheet.subsurface((80, 16, 16, 16)), (64, 64))

        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.luck = 100  # Default luck value (you can adjust this as needed)
        self.luck_bar_color = GREEN  # Fill color of the luck bar
        self.luck_bar_max_width = 100  # Maximum width of the luck bar
        self.luck_bar_height = 10
        self.luck_bar_x = 20  # X-coordinate of the luck bar
        self.luck_bar_y = 20  # Y-coordinate of the luck bar

    def move(self):
        keys = pygame.key.get_pressed()
        # Modify player's speed based on keys pressed
        if keys[pygame.K_a]:
            self.x += (self.base_velocity_x - self.velocity_x)
            self.facing_right = False  # Set the direction to left
            self.sprite = self.running_left_sprites[self.current_sprite_index]  # Use the current running left sprite
            # Reset the stationary sprite update counter when moving
            self.stationary_sprite_update_counter = 0
        elif keys[pygame.K_d]:
            self.x += (self.base_velocity_x + self.velocity_x * 2)
            self.facing_right = True  # Set the direction to right
            self.sprite = self.running_right_sprites[self.current_sprite_index]  # Use the current running right sprite
            # Reset the stationary sprite update counter when moving
            self.stationary_sprite_update_counter = 0

        else:
            # If not moving, adjust player's position based on the base_velocity_x
            self.x += self.base_velocity_x
            # If not moving, use the stationary sprite
            if self.stationary_sprite_update_counter >= self.stationary_sprite_update_frequency:
                self.current_stationary_sprite_index = (self.current_stationary_sprite_index + 1) % len(
                    self.stationary_sprites)
                self.sprite = self.stationary_sprites[self.current_stationary_sprite_index]
                self.stationary_sprite_update_counter = 0  # Reset the stationary sprite counter
            else:
                self.stationary_sprite_update_counter += 1  # Increment the stationary sprite counter

        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.velocity_y = -self.jump_force
            self.is_jumping = True

        if keys[pygame.K_a] or keys[pygame.K_d]:
            if self.sprite_update_counter == self.sprite_update_frequency:
                self.current_sprite_index = (self.current_sprite_index + 1) % len(self.running_right_sprites)
                self.sprite_update_counter = 0  # Reset the counter
            else:
                self.sprite_update_counter += 1  # Increment the counter

        # Update the rect's position
        self.rect.x = self.x
        self.rect.y = self.y

    def apply_gravity(self, gravity, ground, platforms):
        if not self.is_dead:
            # Check if the player is below the top of the game window
            if self.y >= 0:
                self.velocity_y += gravity
                self.y += self.velocity_y
                self.rect.y = self.y  # Update the rectangle's y position

                # Ground check
                if ground.has_tile(self.rect.centerx):  # Check if the player is above a tile
                    if self.y >= ground.top() - self.height + 35:
                        self.y = ground.top() - self.height + 35
                        self.velocity_y = 0
                        self.is_jumping = False

                for platform in platforms:
                    if self.rect.colliderect(platform.rect):
                        # Calculate the player's expected position in the next frame
                        next_position = self.rect.move(0, self.velocity_y)

                        # Check if the next position collides with the platform
                        if next_position.colliderect(platform.rect):
                            # Determine if the player is moving down (falling or not jumping)
                            if self.velocity_y >= 0:
                                # Place the player on top of the platform
                                self.rect.bottom = platform.rect.top
                                self.velocity_y = -2
                                self.is_jumping = False

                self.rect.y = self.y  # Update the rectangle's y position after checking all platforms


            else:
                # If the player is above the top of the game window, reset their position and velocity
                self.y = 0
                self.velocity_y = 0

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))

    def draw_luck_bar(self, screen):
        # Calculate the width of the filled luck bar based on the current luck value
        filled_width = (self.luck / 100) * (self.luck_bar_max_width * 2)  # Double the width

        # Draw "Luck:" text to the left of the bar
        font = pygame.font.Font(None, 36)  # You can adjust the font size as needed
        text = font.render("Luck:", True, BLACK)
        text_rect = text.get_rect()
        text_rect.topleft = (self.luck_bar_x, self.luck_bar_y)

        # Draw the luck bar outline
        pygame.draw.rect(screen, WHITE,
                         (self.luck_bar_x + text_rect.width, self.luck_bar_y, self.luck_bar_max_width * 2,
                          self.luck_bar_height))

        # Draw the filled part of the luck bar
        pygame.draw.rect(screen, self.luck_bar_color,
                         (self.luck_bar_x + text_rect.width, self.luck_bar_y, filled_width, self.luck_bar_height))

        # Blit the "Luck:" text onto the screen
        screen.blit(text, text_rect)
