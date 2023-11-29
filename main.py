import pygame
import sys
from otherEntities import Ground, Button, Platform
from player import Player
from monster import Monster
from logic import handle_game_over_events, reset_game, render_game_over, generate_platform, platforms, mirrors, cats, \
    ladders, render_instructions
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 16 * 5
BACKGROUND_SPEED = 2.5
PLAYER_INITIAL_X = (WIDTH - 50) // 2
PLAYER_INITIAL_Y = HEIGHT - 350 - TILE_SIZE + 35
MONSTER_INITIAL_X = -200
RESTART_BUTTON_WIDTH = 140
RESTART_BUTTON_HEIGHT = 50
RESTART_BUTTON_X = WIDTH // 2 - RESTART_BUTTON_WIDTH // 2
RESTART_BUTTON_Y = HEIGHT // 2
GRAVITY = 1
GRAVITY_ON_DEATH = 0.5
TILE_SIZE = 16 * 5
BLACK = (0, 0, 0)

WHITE = (255, 255, 255)
background_image = pygame.image.load("bg.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Scale it to fit the window

PLATFORM_WIDTH = 150
MIN_PLATFORM_HEIGHT = 100
MAX_PLATFORM_HEIGHT = 300
PLATFORM_SPACING = 300


def main():
    platforms.clear()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("60 FPS Pygame Window with Player and Monster")

    player = Player(PLAYER_INITIAL_X, PLAYER_INITIAL_Y)
    monster = Monster(MONSTER_INITIAL_X, PLAYER_INITIAL_Y - 288 + player.height)
    ground = Ground(HEIGHT - TILE_SIZE)
    restart_button = Button(RESTART_BUTTON_X, RESTART_BUTTON_Y, RESTART_BUTTON_WIDTH, RESTART_BUTTON_HEIGHT, 'Restart')

    game_over = False
    jump_triggered_on_game_over = False
    background_x = 0

    immovable = False
    mirror_fixed_time = None

    last_recorded_x = 0
    high_score = 0

    # Before the game loop
    pygame.font.init()
    font = pygame.font.Font(None, 36)  # You can adjust the font size as needed
    font_color = (255, 255, 255)  # White color for the text

    clock = pygame.time.Clock()
    running = True

    start_time = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()
        if not game_over:
            score = current_time - start_time

        screen.fill(WHITE)
        screen.blit(background_image, (background_x, 0))
        screen.blit(background_image, (background_x + WIDTH, 0))

        font = pygame.font.SysFont(None, 36)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over:

                new_game_over, new_jump_triggered, returned_score = handle_game_over_events(event, restart_button,
                                                                                            player, monster,
                                                                                            ground, score)
                if new_game_over is not None:
                    # Update high score if necessary
                    if returned_score > high_score:
                        high_score = returned_score
                    start_time = pygame.time.get_ticks()
                    platforms.clear()
                    mirrors.clear()
                    cats.clear()
                    ladders.clear()
                    immovable = False
                    game_over = new_game_over
                    jump_triggered_on_game_over = new_jump_triggered
            # Check for 'E' key press to interact with the mirror
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                for mirror in mirrors:
                    if mirror.is_over(player.rect) and mirror.is_broken:
                        mirror.fix()
                        # Set immovable to True and record the timestamp
                        immovable = True
                        mirror_fixed_time = time.time()

        # Inside your main game loop, check if the player should be immovable
        if immovable:
            # Check if 5 seconds (5000 milliseconds) have passed since the mirror was fixed
            if time.time() - mirror_fixed_time >= 1:
                immovable = False  # Player is no longer immovable

        for platform in platforms:
            if platform.rect.right - background_x < 0:
                platforms.remove(platform)

        for mirror in mirrors:
            if mirror.rect.right - background_x < 0:
                mirrors.remove(mirror)

        for cat in cats:
            if cat.rect.right - background_x < 0:
                cats.remove(cat)

        for ladder in ladders:
            if ladder.rect.right - background_x < 0:
                ladders.remove(ladder)

        # Always draw these, regardless of game state
        for platform in platforms:
            platform.draw(screen)

        for mirror in mirrors:
            mirror.draw(screen)

        for cat in cats:
            cat.draw(screen)

        for ladder in ladders:
            ladder.draw(screen)

        if game_over:
            render_instructions(screen, font)
            player.apply_gravity(gravity=GRAVITY_ON_DEATH, ground=ground, platforms=platforms)

            if not jump_triggered_on_game_over:
                player.velocity_y = -player.jump_force
                jump_triggered_on_game_over = True
            render_game_over(screen, restart_button)
        else:
            background_x -= BACKGROUND_SPEED
            if background_x <= -WIDTH:
                background_x = 0
            generate_platform()
            for platform in platforms:
                platform.update()
            for mirror in mirrors:
                mirror.update()
                # Check for collision with the monster
                if mirror.rect.colliderect(monster.rect):
                    if mirror.is_broken:
                        if not mirror.passed_monster:
                            # Reduce player's luck by 10%
                            mirror.passed_monster = True
                            player.luck -= 10
                            if player.luck <= 0:
                                game_over = True
            for ladder in ladders:
                ladder.update()
                if ladder.rect.colliderect(player.rect):
                    if not ladder.passed_player:
                        # Reduce player's luck by 10%
                        ladder.passed_player = True
                        player.luck -= 10
                        if player.luck <= 0:
                            game_over = True

            for cat in cats:
                cat.update()
                if cat.rect.colliderect(player.rect):
                    if not cat.passed_player:
                        # Reduce player's luck by 10%
                        cat.passed_player = True
                        player.luck -= 10
                        if player.luck <= 0:
                            game_over = True
            if immovable:
                # Display "Fixing mirror..." over the player's head
                text = font.render("Fixing mirror...", True, font_color)
                text_rect = text.get_rect()
                text_rect.center = (player.rect.centerx, player.rect.y - 20)
                screen.blit(text, text_rect)
                player.rect.x -= 5
                player.x -= 5
            else:
                player.move()
            player.apply_gravity(gravity=GRAVITY, ground=ground, platforms=platforms)
            if player.y > HEIGHT:
                game_over = True
                player.is_dead = True

            ground.update()

            if monster.collides_with(player):
                game_over = True
                player.is_dead = True
                monster.attacks = True
                monster.current_frame = 0
                player.move()
                player.sprite = player.death_sprite

        player.draw(screen)
        monster.draw(screen)
        ground.draw(screen)
        player.draw_luck_bar(screen)

        # Display current score
        score_label = font.render(f"Score: {int(score)}", True, BLACK)

        screen.blit(score_label, (WIDTH / 2, 50))

        # Display high score above current score
        high_score_label = font.render(f"High Score: {int(high_score)}", True, BLACK)
        screen.blit(high_score_label,
                    (WIDTH / 2, high_score_label.get_height() - 5))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
