import pygame
import random
from otherEntities import Platform, Mirror, Cat, Ladder

WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 16 * 5
PLAYER_INITIAL_X = (WIDTH - 50) // 2
PLAYER_INITIAL_Y = HEIGHT - 60 - TILE_SIZE + 35
BLACK = (0, 0, 0)
MAX_PLATFORMS = 10
MAX_MIRRORS = 10
BLUE = (0, 0, 255)

platforms = []
mirrors = []
ladders = []
cats = []


def generate_platform():
    if len(platforms) == 0:
        # Create the first platform at a fixed position
        platform = Platform(700, 500, 1)
        platforms.append(platform)
    elif len(platforms) < MAX_PLATFORMS:
        last_platform = platforms[-1]  # get the last platform

        p_width = random.randint(1, 5)
        p_x = last_platform.rect.x + last_platform.total_width + random.randint(100, 300)
        p_y = random.randint(100, 500)  # adjust for vertical variation

        platform = Platform(p_x, p_y, p_width)

        # Add logic to randomly determine if an object should be placed on the platform
        if random.choices([True, False], [0.75, 0.25]):
            object_x = random.randint(p_x, p_x + platform.total_width)

            # Randomly choose between a mirror, a cat, and a ladder
            object_type = random.choices(["mirror", "cat", "ladder"], weights=[50, 25, 25])[0]

            if object_type == "mirror":
                # Create an instance of the Mirror class with broken and fixed images
                object_y = p_y - 64
                mirror = Mirror(object_x, object_y)
                mirrors.append(mirror)
            elif object_type == "cat":
                # Create an instance of the Cat class with the cat sprite
                object_y = p_y - 60
                cat = Cat(object_x, object_y)
                cats.append(cat)
            elif object_type == "ladder":
                object_y = p_y - 192
                # Create an instance of the Ladder class with a ladder sprite
                ladder = Ladder(object_x, object_y)  # Adjust ladder height as needed
                ladders.append(ladder)

        platforms.append(platform)


def handle_game_over_events(event, restart_button, player, monster, ground, current_score):
    if event.type == pygame.MOUSEBUTTONDOWN and restart_button.is_over(pygame.mouse.get_pos()):
        new_game_over, new_jump_triggered = reset_game(player, monster, ground)
        return new_game_over, new_jump_triggered, current_score

    return None, None, None


def reset_game(player, monster, ground):
    player.__init__(PLAYER_INITIAL_X, PLAYER_INITIAL_Y)
    player.is_dead = False
    player.is_jumping = False
    monster.attacks = False
    monster.is_moving = True

    # Reset the first 20 blocks of ground to be solid
    ground.tiles[:20] = [True for _ in range(20)]

    return False, False  # returns game_over, jump_triggered_on_game_over


def render_game_over(screen, restart_button):
    font = pygame.font.SysFont(None, 72)
    label = font.render("Game Over!", True, BLACK)
    screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 4))
    restart_button.draw(screen)


def render_instructions(screen, font):
    instructions = [
        "Press E to fix mirrors.",
        "Avoid all cats and ladders.",
        "Don't let the monster catch you."
    ]

    # Set the starting y-position for the instructions
    y_position = 450  # or any other value where you want the instructions to start
    x_position = 500

    for instruction in instructions:
        label = font.render(instruction, True, BLUE)  # Assuming BLACK is the color of your text
        screen.blit(label, (x_position, y_position))
        y_position += label.get_height() + 10  # 10 pixels spacing between instructions
