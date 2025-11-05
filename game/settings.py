"""Game configuration and constant values for the survival RPG prototype."""
from __future__ import annotations

import pygame

# Screen configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# World configuration
TILE_SIZE = 64
WORLD_WIDTH = 64  # tiles
WORLD_HEIGHT = 64  # tiles

# Player stats
MAX_HEALTH = 100
MAX_HUNGER = 100
MAX_THIRST = 100
MAX_STAMINA = 100
MAX_SANITY = 100

# Depletion rates (per second)
HUNGER_DEPLETION = 0.8
THIRST_DEPLETION = 1.2
STAMINA_RECOVERY = 18
SANITY_DEPLETION = 0.25

# Regeneration thresholds
RESTORE_THRESHOLD = 70
HEALTH_REGEN_RATE = 4
SANITY_REGEN_NEAR_FIRE = 15

# Colors
JUNGLE_GREEN = pygame.Color(34, 139, 34)
DARK_JUNGLE = pygame.Color(6, 60, 20)
SKY_BLUE = pygame.Color(135, 206, 235)
SUNSET_ORANGE = pygame.Color(255, 140, 0)
NIGHT_BLUE = pygame.Color(10, 10, 40)
MIST_GRAY = pygame.Color(180, 205, 205)
HUD_BACKGROUND = pygame.Color(20, 20, 20, 200)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(200, 60, 60)
YELLOW = pygame.Color(255, 220, 90)
SKY_PURPLE = pygame.Color(125, 86, 200)
WATER_BLUE = pygame.Color(44, 125, 192)
GROUND_BROWN = pygame.Color(93, 64, 55)
RUIN_STONE = pygame.Color(140, 140, 160)
CLEARING_GREEN = pygame.Color(58, 140, 63)

TILE_COLORS = {
    "forest": JUNGLE_GREEN,
    "clearing": CLEARING_GREEN,
    "water": WATER_BLUE,
    "ruin": RUIN_STONE,
    "bog": pygame.Color(48, 87, 56),
}

# Crafting recipes
CRAFTING_RECIPES: dict[str, dict[str, int]] = {
    "stone_knife": {"stone": 2, "fiber": 1},
    "hand_axe": {"wood": 2, "stone": 1},
    "rope": {"fiber": 3},
    "torch": {"wood": 1, "resin": 1},
    "bandage": {"fiber": 2, "herb": 1},
    "cooked_meat": {"raw_meat": 1},
}

STRUCTURE_RECIPES: dict[str, dict[str, int]] = {
    "campfire": {"wood": 4, "stone": 2},
    "water_collector": {"wood": 3, "fiber": 3, "resin": 1},
    "lean_to": {"wood": 5, "rope": 2, "fiber": 2},
    "garden_plot": {"wood": 2, "fiber": 2, "water": 1},
}

STRUCTURE_COLORS = {
    "campfire": pygame.Color(255, 120, 60),
    "water_collector": pygame.Color(90, 160, 255),
    "lean_to": pygame.Color(140, 100, 50),
    "garden_plot": pygame.Color(120, 190, 90),
}

STRUCTURE_EFFECTS = {
    "campfire": {"warmth_radius": 120, "sanity": 4},
    "water_collector": {"supply_interval": 18, "resource": "water", "amount": 1},
    "lean_to": {"rest_radius": 100, "stamina": 12},
    "garden_plot": {"harvest_interval": 30, "resource": "food", "amount": 2},
}

# Resource spawn probabilities
RESOURCE_SPAWN_WEIGHTS = {
    "wood": 0.34,
    "stone": 0.22,
    "water": 0.18,
    "food": 0.14,
    "fiber": 0.07,
    "resin": 0.04,
    "herb": 0.05,
}

RESOURCE_RESPAWN_TIME = 45

# Wildlife spawn chances
WILDLIFE_SPAWN_CHANCE = 0.06
WILDLIFE_SPEED_RANGE = (35, 65)

# Day / night cycle duration in seconds
DAY_LENGTH = 240

# Weather settings
WEATHER_DURATION = (35, 70)
WEATHER_TYPES = ("clear", "rain", "mist")
RAIN_THIRST_MODIFIER = 0.6
MIST_SANITY_BONUS = 0.1

# Input mappings
MOVE_KEYS = {
    pygame.K_w: pygame.Vector2(0, -1),
    pygame.K_s: pygame.Vector2(0, 1),
    pygame.K_a: pygame.Vector2(-1, 0),
    pygame.K_d: pygame.Vector2(1, 0),
}

INTERACT_KEY = pygame.K_e
SPRINT_KEY = pygame.K_LSHIFT
INVENTORY_KEY = pygame.K_TAB
PAUSE_KEY = pygame.K_ESCAPE
CRAFT_KEY = pygame.K_c
BUILD_KEY = pygame.K_b
ATTACK_KEY = pygame.K_SPACE

# Camera
CAMERA_MARGIN = 150

# Quest configuration
QUEST_REWARDS = {
    "wood_gathering": {"fiber": 2},
    "first_fire": {"raw_meat": 1},
    "secure_water": {"resin": 1, "fiber": 1},
}
