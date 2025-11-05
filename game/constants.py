import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
FONT_NAME = "arial"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 50)
LIGHT_GREY = (200, 200, 200)
ACCENT = (123, 104, 238)
WARNING = (240, 128, 128)
SUCCESS = (110, 180, 120)

PANEL_BG = (24, 24, 32)
BUTTON_BG = (70, 70, 90)
BUTTON_HOVER = (100, 100, 140)

UI_PADDING = 16
PANEL_MARGIN = 12

RESOURCE_TYPES = ["stardust", "essence", "crystal", "herbs"]

STAT_MAX = 100
CARE_DECAY_PER_SECOND = {
    "hunger": 0.8,
    "thirst": 0.9,
    "mood": 0.6,
    "energy": 0.5,
}

TASK_DURATION = {
    "forage": 20,
    "gather": 25,
    "scout": 30,
}

BREEDING_DURATION = 35
EGG_HATCH_TIME = 25

COMBAT_ACTIONS = ["Strike", "Channel", "Guard", "Heal"]

pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont(FONT_NAME, 20)
SMALL_FONT = pygame.font.SysFont(FONT_NAME, 16)
LARGE_FONT = pygame.font.SysFont(FONT_NAME, 28)
TITLE_FONT = pygame.font.SysFont(FONT_NAME, 48)
