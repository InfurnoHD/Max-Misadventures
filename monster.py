import pygame

# Screen dimensions
WIDTH, HEIGHT = 1280, 720

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Load monster sprite sheet
monster_spritesheet = pygame.image.load("Run.png")
monster_attack_spritesheet = pygame.image.load("Attack_1.png")

# Extract monster animation frames
monster_frames = [
    pygame.transform.scale(monster_spritesheet.subsurface((i * 96, 0, 96, 96)), (576, 576)) for i in range(6)
]

monster_attack = [
    pygame.transform.scale(monster_attack_spritesheet.subsurface((0 * 96, 0, 96, 96)), (576, 576)),  # Sprite 1
    pygame.transform.scale(monster_attack_spritesheet.subsurface((1 * 96, 0, 96, 96)), (576, 576)),  # Sprite 2
    pygame.transform.scale(monster_attack_spritesheet.subsurface((2 * 96, 0, 96, 96)), (576, 576)),  # Sprite 3
    pygame.transform.scale(monster_attack_spritesheet.subsurface((3 * 96, 0, 96, 96)), (576, 576))  # Sprite 4
]


class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 576
        self.height = 576
        self.current_frame = 0
        self.frame_counter = 0
        self.animation_speed = 5  # Adjust animation speed as needed
        self.attacks = False
        self.is_moving = True  # Initialize the is_moving attribute to True

        # Create a rect for the monster
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def animate(self):
        # When attacking, we should always allow animation even if is_moving is False
        if not self.is_moving and not self.attacks:
            return

        # Update the frame counter
        self.frame_counter += 1

        if self.attacks:
            # If attacking, consider the length of monster_attack
            if self.frame_counter >= self.animation_speed:
                self.current_frame += 1
                if self.current_frame >= len(monster_attack):
                    self.attacks = False  # Reset the attack flag when the attack animation is over
                    self.current_frame = 0
                self.frame_counter = 0
        else:
            # Otherwise, consider the length of monster_frames for idle/running animation
            if self.frame_counter >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(monster_frames)
                self.frame_counter = 0

    def draw(self, screen):
        self.animate()  # Call animate to update the frame
        if not self.attacks:
            screen.blit(monster_frames[self.current_frame], (self.x, self.y))
        else:
            screen.blit(monster_attack[self.current_frame], (self.x, self.y))

    def collides_with(self, player):
        # Shrink the hitbox by 25%
        shrink_factor = 0.75
        shrunk_width = self.width * shrink_factor
        shrunk_height = self.height

        # Calculate the center point of the shrunk hitbox
        shrunk_center_x = self.x + (self.width / 2) * (1 - shrink_factor)
        shrunk_center_y = self.y + (self.height / 2) * (1 - shrink_factor)

        # Calculate the player's center point
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2

        # Check for collision with the shrunk hitbox
        collision_detected = (shrunk_center_x < player_center_x + player.width and
                              shrunk_center_x + shrunk_width > player_center_x and
                              shrunk_center_y < player_center_y + player.height and
                              shrunk_center_y + shrunk_height > player_center_y)

        if collision_detected:
            self.is_moving = False  # Stop the monster's movement after collision

        return collision_detected

