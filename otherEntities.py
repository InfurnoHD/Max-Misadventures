import random

import pygame

# Screen dimensions
WIDTH, HEIGHT = 1280, 720

# Colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Load the spritesheet
spritesheet = pygame.image.load("ground3T.png")

TILE_SIZE = 16 * 5  # Scale up by a factor of 5
ground_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
ground_sprite.blit(pygame.transform.scale(spritesheet, (spritesheet.get_width() * 5, spritesheet.get_height() * 5)),
                   (0, 0), (TILE_SIZE, 0, TILE_SIZE * 2, TILE_SIZE))

platform_middle = pygame.transform.scale(pygame.image.load("platmiddle.png"), (64, 64))
platform_left = pygame.transform.scale(pygame.image.load("platleft.png"), (64, 64))
platform_right = pygame.transform.scale(pygame.image.load("platright.png"), (64, 64))


class Cat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64  # Adjust the width and height as needed
        self.height = 64
        self.sprite = pygame.image.load("cat.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite.subsurface((0, 0, 32, 32)), (64, 64))
        self.rect = pygame.Rect(x, y, self.sprite.get_width(), self.sprite.get_height())
        self.rect.x = x
        self.rect.y = y
        self.passed_player = False

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.rect.x -= 5
        self.x -= 5


class Ladder:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16  # Adjust the width to match the sprite's width
        self.height = 48
        self.sprite = pygame.image.load("ladder.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite.subsurface((192, 16, 16, 48)), (64, 192))
        self.rect = pygame.Rect(x, y, self.sprite.get_width(), self.sprite.get_height())
        self.rect.x = x
        self.rect.y = y
        self.passed_player = False

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))

    def update(self):
        self.rect.x -= 5
        self.x -= 5



class Mirror:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.broken_image = pygame.transform.scale(pygame.image.load("mirror_broken.png"), (64, 64))
        self.fixed_image = pygame.transform.scale(pygame.image.load("mirror.png"), (64, 64))
        self.is_broken = True  # The mirror starts as broken
        self.rect = pygame.Rect(x, y, self.broken_image.get_width(), self.broken_image.get_height())
        self.rect.x = x
        self.rect.y = y
        self.passed_monster = False

    def draw(self, screen):
        if self.is_broken:
            screen.blit(self.broken_image, (self.x, self.y))
        else:
            screen.blit(self.fixed_image, (self.x, self.y))

    def is_over(self, player_rect):
        return self.rect.colliderect(player_rect)

    def fix(self):
        if self.is_broken:
            # Perform any logic for fixing the mirror here
            # For example, change the mirror's state to fixed
            self.is_broken = False
            self.rect = pygame.Rect(self.x, self.y, self.fixed_image.get_width(), self.fixed_image.get_height())

    def update(self):
        self.rect.x -= 5
        self.x -= 5


class Platform:
    def __init__(self, x, y, amt_middle):
        self.total_width = (
                platform_left.get_width()
                + (amt_middle * platform_middle.get_width())
                + platform_right.get_width()
        )
        self.image = pygame.Surface((self.total_width, platform_left.get_height()), pygame.SRCALPHA)
        self.image.blit(platform_left, (0, 0))
        for i in range(amt_middle):
            self.image.blit(platform_middle, (platform_left.get_width() + i * platform_middle.get_width(), 0))
        self.image.blit(platform_right, (self.total_width - platform_right.get_width(), 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        self.rect.x -= 5

    def top(self):
        return self.rect.y


class Ground:
    def __init__(self, y):
        self.y = y
        self.x_offset = 0  # Offset for moving the ground to the left

        # Ensure the first 20 tiles always spawn
        self.tiles = [True for _ in range(20)]

        # The rest of the tiles can have a random chance to spawn
        self.tiles.extend([random.choice([True, False]) for _ in range(WIDTH // TILE_SIZE + 2 - 20)])

    def update(self):
        # Move the ground to the left
        self.x_offset -= 5
        if self.x_offset <= -TILE_SIZE:
            self.x_offset = 0
            # Rotate the tile states
            self.tiles.pop(0)
            self.tiles.append(random.choice([True, False]))

    def draw(self, screen):
        for idx, x in enumerate(range(self.x_offset, WIDTH, TILE_SIZE)):
            if self.tiles[idx]:  # Check tile state
                screen.blit(ground_sprite, (x, self.y))
        # Draw additional tiles if needed to fill the screen
        for idx, x in enumerate(range(self.x_offset - TILE_SIZE, 0, TILE_SIZE)):
            if self.tiles[idx]:  # Check tile state
                screen.blit(ground_sprite, (x, self.y))

    def top(self):
        return self.y

    def has_tile(self, x):
        # Given an x-coordinate, determine which tile it's over
        tile_index = (x - self.x_offset) // TILE_SIZE

        # Ensure index is within bounds
        if 0 <= tile_index < len(self.tiles):
            return self.tiles[tile_index]
        return False


class Button:
    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont(None, 36)
        label = font.render(self.text, True, BLACK)
        screen.blit(label, (
            self.x + (self.width // 2 - label.get_width() // 2), self.y + (self.height // 2 - label.get_height() // 2)))

    def is_over(self, pos):
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height
