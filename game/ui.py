from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import pygame

from .constants import BUTTON_BG, BUTTON_HOVER, DEFAULT_FONT, PANEL_BG, WHITE


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    callback: Callable[[], None]
    enabled: bool = True
    tooltip: Optional[str] = None

    def draw(self, surface: pygame.Surface, mouse_pos: Tuple[int, int]) -> None:
        color = BUTTON_HOVER if self.rect.collidepoint(mouse_pos) and self.enabled else BUTTON_BG
        if not self.enabled:
            color = [int(c * 0.4) for c in color]
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        text_surface = DEFAULT_FONT.render(self.label, True, WHITE if self.enabled else (180, 180, 180))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.enabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()


def draw_panel(surface: pygame.Surface, rect: pygame.Rect, title: Optional[str] = None) -> None:
    pygame.draw.rect(surface, PANEL_BG, rect)
    if title:
        title_surface = DEFAULT_FONT.render(title, True, WHITE)
        surface.blit(title_surface, (rect.x + 8, rect.y + 8))


def draw_text(surface: pygame.Surface, text: str, pos: Tuple[int, int], color: Tuple[int, int, int] = WHITE, font=DEFAULT_FONT) -> None:
    surface.blit(font.render(text, True, color), pos)
