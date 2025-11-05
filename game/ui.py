"""Heads-up display and simple interfaces for the survival RPG prototype."""
from __future__ import annotations

from typing import Dict, Iterable

import pygame

from . import settings


class HUD:
    def __init__(self, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
        self.font = font
        self.small_font = small_font

    def draw_bar(
        self,
        surface: pygame.Surface,
        label: str,
        value: float,
        maximum: float,
        color: pygame.Color,
        position: tuple[int, int],
    ) -> None:
        x, y = position
        width, height = 220, 20
        pygame.draw.rect(surface, settings.HUD_BACKGROUND, (x - 4, y - 4, width + 8, height + 8))
        pygame.draw.rect(surface, settings.WHITE, (x - 4, y - 4, width + 8, height + 8), 2)
        fill_width = int(width * max(0, min(1, value / maximum)))
        pygame.draw.rect(surface, color, (x, y, fill_width, height))
        text_surface = self.small_font.render(f"{label}: {int(value)} / {int(maximum)}", True, settings.WHITE)
        surface.blit(text_surface, (x, y - 22))

    def draw_inventory(self, surface: pygame.Surface, inventory: Dict[str, int]) -> None:
        bg_rect = pygame.Rect(20, 200, 260, 320)
        pygame.draw.rect(surface, settings.HUD_BACKGROUND, bg_rect)
        pygame.draw.rect(surface, settings.WHITE, bg_rect, 2)
        title = self.font.render("Inventory", True, settings.WHITE)
        surface.blit(title, (bg_rect.x + 12, bg_rect.y + 12))
        for index, (item, amount) in enumerate(sorted(inventory.items())):
            text = self.small_font.render(f"{item}: {amount}", True, settings.WHITE)
            surface.blit(text, (bg_rect.x + 12, bg_rect.y + 40 + index * 20))

    def draw_crafting(
        self,
        surface: pygame.Surface,
        recipes: Dict[str, Dict[str, int]],
        inventory: Dict[str, int],
        hotkey_offset: int = 1,
    ) -> None:
        bg_rect = pygame.Rect(20, 540, 360, 240)
        pygame.draw.rect(surface, settings.HUD_BACKGROUND, bg_rect)
        pygame.draw.rect(surface, settings.WHITE, bg_rect, 2)
        title = self.font.render("Crafting (number keys)", True, settings.WHITE)
        surface.blit(title, (bg_rect.x + 12, bg_rect.y + 12))
        for index, (recipe_name, cost) in enumerate(recipes.items()):
            parts = ", ".join(f"{item} x{amount}" for item, amount in cost.items())
            affordable = all(inventory.get(item, 0) >= amount for item, amount in cost.items())
            text_color = settings.YELLOW if affordable else settings.RED
            text = self.small_font.render(f"[{index + hotkey_offset}] {recipe_name}: {parts}", True, text_color)
            surface.blit(text, (bg_rect.x + 12, bg_rect.y + 44 + index * 22))

    def draw_messages(self, surface: pygame.Surface, messages: list[str]) -> None:
        for index, message in enumerate(messages[-6:]):
            text = self.small_font.render(message, True, settings.WHITE)
            surface.blit(text, (20, settings.SCREEN_HEIGHT - 28 * (index + 1)))

    def draw_weather(self, surface: pygame.Surface, weather: str, timer: float) -> None:
        remaining = max(0, int(timer))
        text = self.small_font.render(f"Weather: {weather.title()} ({remaining}s)", True, settings.WHITE)
        surface.blit(text, (settings.SCREEN_WIDTH - 260, 50))

    def draw_quest_log(self, surface: pygame.Surface, objectives: Iterable[str]) -> None:
        bg_rect = pygame.Rect(settings.SCREEN_WIDTH - 340, 140, 300, 140)
        pygame.draw.rect(surface, settings.HUD_BACKGROUND, bg_rect)
        pygame.draw.rect(surface, settings.WHITE, bg_rect, 2)
        title = self.font.render("Objectives", True, settings.WHITE)
        surface.blit(title, (bg_rect.x + 12, bg_rect.y + 12))
        for index, line in enumerate(objectives):
            text = self.small_font.render(line, True, settings.WHITE)
            surface.blit(text, (bg_rect.x + 12, bg_rect.y + 44 + index * 22))

    def draw_build_panel(self, surface: pygame.Surface, structures: list[str], selected: int) -> None:
        bg_rect = pygame.Rect(settings.SCREEN_WIDTH - 360, settings.SCREEN_HEIGHT - 200, 340, 170)
        pygame.draw.rect(surface, settings.HUD_BACKGROUND, bg_rect)
        pygame.draw.rect(surface, settings.WHITE, bg_rect, 2)
        title = self.font.render("Build Mode", True, settings.WHITE)
        surface.blit(title, (bg_rect.x + 12, bg_rect.y + 12))
        for index, name in enumerate(structures):
            prefix = "->" if index == selected else "  "
            cost = settings.STRUCTURE_RECIPES[name]
            cost_text = ", ".join(f"{item}x{amount}" for item, amount in cost.items())
            color = settings.YELLOW if index == selected else settings.WHITE
            text = self.small_font.render(f"{prefix} {name}: {cost_text}", True, color)
            surface.blit(text, (bg_rect.x + 12, bg_rect.y + 44 + index * 22))
        controls = "Arrows: select  Enter: place  B: exit"
        control_text = self.small_font.render(controls, True, settings.WHITE)
        surface.blit(control_text, (bg_rect.x + 12, bg_rect.y + bg_rect.height - 28))


class PauseOverlay:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font

    def draw(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        text = self.font.render("Paused", True, settings.WHITE)
        rect = text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        surface.blit(text, rect)
