"""Player entity and stat management for the survival RPG prototype."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import pygame

from . import settings


@dataclass
class Player:
    """Top-down character controlled by the player."""

    position: pygame.Vector2
    speed: float = 220.0
    sprint_multiplier: float = 1.5
    health: float = settings.MAX_HEALTH
    hunger: float = settings.MAX_HUNGER
    thirst: float = settings.MAX_THIRST
    stamina: float = settings.MAX_STAMINA
    sanity: float = settings.MAX_SANITY
    inventory: Dict[str, int] = field(
        default_factory=lambda: {
            "wood": 0,
            "stone": 0,
            "fiber": 0,
            "resin": 0,
            "water": 0,
            "food": 0,
            "herb": 0,
            "raw_meat": 0,
            "bandage": 0,
            "cooked_meat": 0,
            "torch": 0,
            "rope": 0,
            "hand_axe": 0,
            "stone_knife": 0,
        }
    )
    equipped_tool: str | None = None
    facing: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 1))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.position.x, self.position.y, settings.TILE_SIZE // 2, settings.TILE_SIZE // 2)

    def move(self, dt: float, keys: pygame.key.ScancodeWrapper, collision: pygame.Rect) -> None:
        direction = pygame.Vector2(0, 0)
        for key, vector in settings.MOVE_KEYS.items():
            if keys[key]:
                direction += vector
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.facing = direction
        is_sprinting = keys[settings.SPRINT_KEY] and self.stamina > 0
        multiplier = self.sprint_multiplier if is_sprinting else 1.0
        velocity = direction * self.speed * multiplier * dt
        next_position = self.position + velocity
        next_rect = pygame.Rect(next_position.x, next_position.y, self.rect().width, self.rect().height)
        if collision.contains(next_rect):
            self.position = next_position
        else:
            clamped_x = max(collision.left, min(next_rect.left, collision.right - next_rect.width))
            clamped_y = max(collision.top, min(next_rect.top, collision.bottom - next_rect.height))
            self.position.update(clamped_x, clamped_y)
        if is_sprinting and direction.length_squared() > 0:
            self.stamina = max(0, self.stamina - 25 * dt)
        else:
            self.stamina = min(settings.MAX_STAMINA, self.stamina + settings.STAMINA_RECOVERY * dt)

    def update_vitals(self, dt: float, weather: str) -> None:
        hunger_drain = settings.HUNGER_DEPLETION * dt
        thirst_drain = settings.THIRST_DEPLETION * dt
        sanity_drain = settings.SANITY_DEPLETION * dt
        if weather == "rain":
            thirst_drain *= settings.RAIN_THIRST_MODIFIER
        elif weather == "mist":
            sanity_drain = max(0, sanity_drain - settings.MIST_SANITY_BONUS * dt)
        self.hunger = max(0, self.hunger - hunger_drain)
        self.thirst = max(0, self.thirst - thirst_drain)
        self.sanity = max(0, self.sanity - sanity_drain)
        if self.hunger <= 0 or self.thirst <= 0:
            self.health = max(0, self.health - 12 * dt)
        elif (
            self.health < settings.MAX_HEALTH
            and self.hunger > settings.RESTORE_THRESHOLD
            and self.thirst > settings.RESTORE_THRESHOLD
        ):
            self.health = min(settings.MAX_HEALTH, self.health + settings.HEALTH_REGEN_RATE * dt)

    def consume(self, item: str) -> bool:
        if self.inventory.get(item, 0) <= 0:
            return False
        self.inventory[item] -= 1
        if item == "food":
            self.hunger = min(settings.MAX_HUNGER, self.hunger + 30)
            self.sanity = min(settings.MAX_SANITY, self.sanity + 4)
        elif item == "water":
            self.thirst = min(settings.MAX_THIRST, self.thirst + 40)
        elif item == "herb":
            self.health = min(settings.MAX_HEALTH, self.health + 18)
            self.sanity = min(settings.MAX_SANITY, self.sanity + 8)
        elif item == "bandage":
            self.health = min(settings.MAX_HEALTH, self.health + 25)
        elif item == "cooked_meat":
            self.hunger = min(settings.MAX_HUNGER, self.hunger + 50)
            self.health = min(settings.MAX_HEALTH, self.health + 10)
        return True

    def add_item(self, item: str, amount: int = 1) -> None:
        self.inventory[item] = self.inventory.get(item, 0) + amount

    def has_resources(self, cost: Dict[str, int]) -> bool:
        return all(self.inventory.get(resource, 0) >= amount for resource, amount in cost.items())

    def craft(self, recipe_name: str, nearby_structures: set[str]) -> bool:
        recipe = settings.CRAFTING_RECIPES.get(recipe_name)
        if not recipe or not self.has_resources(recipe):
            return False
        if recipe_name == "cooked_meat" and "campfire" not in nearby_structures:
            return False
        for resource, amount in recipe.items():
            self.inventory[resource] -= amount
        self.inventory[recipe_name] = self.inventory.get(recipe_name, 0) + 1
        return True

    def rest(self, dt: float, stamina_bonus: float = 0.0, sanity_bonus: float = 0.0) -> None:
        """Recover stamina and sanity while resting near supportive structures."""

        stamina_rate = 25 + stamina_bonus
        sanity_rate = 2 + sanity_bonus
        self.stamina = min(settings.MAX_STAMINA, self.stamina + stamina_rate * dt)
        self.sanity = min(settings.MAX_SANITY, self.sanity + sanity_rate * dt)
