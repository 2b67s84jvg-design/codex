"""Simple camera tracking the player within the world bounds."""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from . import settings


@dataclass
class Camera:
    """Keep the viewport centered around a focus rect."""

    width: int
    height: int
    world_width: int
    world_height: int
    offset: pygame.Vector2 = pygame.Vector2(0, 0)

    def update(self, target: pygame.Rect) -> None:
        desired_x = target.centerx - self.width // 2
        desired_y = target.centery - self.height // 2
        clamp_x = max(0, min(desired_x, self.world_width - self.width))
        clamp_y = max(0, min(desired_y, self.world_height - self.height))
        self.offset.update(clamp_x, clamp_y)

    def apply(self, position: pygame.Vector2 | tuple[float, float]) -> pygame.Vector2:
        if isinstance(position, pygame.Vector2):
            return position - self.offset
        return pygame.Vector2(position[0] - self.offset.x, position[1] - self.offset.y)

    def screen_rect(self) -> pygame.Rect:
        return pygame.Rect(self.offset.x, self.offset.y, self.width, self.height)


def world_pixel_size() -> tuple[int, int]:
    return settings.WORLD_WIDTH * settings.TILE_SIZE, settings.WORLD_HEIGHT * settings.TILE_SIZE
