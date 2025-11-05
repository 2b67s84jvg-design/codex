"""Procedural world generation and entity management."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List

import pygame

from . import settings
from .camera import Camera, world_pixel_size

RESOURCE_COLORS = {
    "wood": pygame.Color(101, 67, 33),
    "stone": pygame.Color(120, 120, 120),
    "water": pygame.Color(64, 164, 223),
    "food": pygame.Color(205, 133, 63),
    "fiber": pygame.Color(85, 107, 47),
    "herb": pygame.Color(154, 205, 50),
    "resin": pygame.Color(184, 134, 11),
}


@dataclass
class ResourceNode:
    position: pygame.Vector2
    resource_type: str
    quantity: int
    respawn_timer: float = 0.0

    def rect(self) -> pygame.Rect:
        size = settings.TILE_SIZE // 1.5
        return pygame.Rect(self.position.x, self.position.y, size, size)


@dataclass
class Wildlife:
    position: pygame.Vector2
    wander_radius: float = 180
    speed: float = field(
        default_factory=lambda: random.uniform(*settings.WILDLIFE_SPEED_RANGE)
    )
    direction: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(1, 0))

    def rect(self) -> pygame.Rect:
        size = settings.TILE_SIZE // 2
        return pygame.Rect(self.position.x, self.position.y, size, size)

    def update(self, dt: float, bounds: pygame.Rect) -> None:
        if random.random() < 0.02:
            angle = random.uniform(0, 360)
            self.direction = pygame.Vector2(1, 0).rotate(angle)
        self.position += self.direction * self.speed * dt
        rect = self.rect()
        if not bounds.contains(rect):
            if rect.left < bounds.left or rect.right > bounds.right:
                self.direction.x *= -1
            if rect.top < bounds.top or rect.bottom > bounds.bottom:
                self.direction.y *= -1
            self.position.x = max(bounds.left, min(self.position.x, bounds.right - rect.width))
            self.position.y = max(bounds.top, min(self.position.y, bounds.bottom - rect.height))


@dataclass
class Structure:
    position: pygame.Vector2
    structure_type: str
    timer: float = 0.0
    storage: dict[str, int] = field(default_factory=dict)

    def rect(self) -> pygame.Rect:
        size = int(settings.TILE_SIZE * 0.9)
        return pygame.Rect(self.position.x, self.position.y, size, size)


class World:
    """Container for all world objects."""

    def __init__(self) -> None:
        width, height = world_pixel_size()
        self.surface = pygame.Surface((width, height))
        self.bounds = pygame.Rect(0, 0, width, height)
        self.tiles: list[list[str]] = self._generate_tiles()
        self._draw_base_layer()
        self.resource_nodes: List[ResourceNode] = []
        self.wildlife: List[Wildlife] = []
        self.structures: List[Structure] = []
        self.weather: str = "clear"
        self.weather_timer: float = random.uniform(*settings.WEATHER_DURATION)
        self._spawn_resources()
        self._spawn_wildlife()

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------
    def _generate_tiles(self) -> list[list[str]]:
        rng = random.Random()
        tiles: list[list[str]] = []
        for y in range(settings.WORLD_HEIGHT):
            row: list[str] = []
            for x in range(settings.WORLD_WIDTH):
                noise = (
                    0.4 * math.sin(x * 0.15)
                    + 0.4 * math.cos(y * 0.12)
                    + 0.2 * math.sin((x + y) * 0.07)
                    + rng.random()
                ) / 2.0
                if noise < 0.22:
                    tile = "water"
                elif noise < 0.32:
                    tile = "bog"
                elif noise > 0.75:
                    tile = "ruin"
                elif noise > 0.6:
                    tile = "clearing"
                else:
                    tile = "forest"
                row.append(tile)
            tiles.append(row)
        return tiles

    def _draw_base_layer(self) -> None:
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                color = settings.TILE_COLORS.get(tile, settings.GROUND_BROWN)
                rect = pygame.Rect(
                    x * settings.TILE_SIZE,
                    y * settings.TILE_SIZE,
                    settings.TILE_SIZE,
                    settings.TILE_SIZE,
                )
                pygame.draw.rect(self.surface, color, rect)

    def _spawn_resources(self) -> None:
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile == "water":
                    continue
                if random.random() < settings.RESOURCE_SPAWN_WEIGHTS.get("wood", 0) / 6:
                    position = pygame.Vector2(
                        x * settings.TILE_SIZE + random.randint(8, 24),
                        y * settings.TILE_SIZE + random.randint(8, 24),
                    )
                    resource_type = random.choices(
                        population=list(settings.RESOURCE_SPAWN_WEIGHTS.keys()),
                        weights=settings.RESOURCE_SPAWN_WEIGHTS.values(),
                        k=1,
                    )[0]
                    quantity = random.randint(1, 4)
                    self.resource_nodes.append(ResourceNode(position, resource_type, quantity))

    def _spawn_wildlife(self) -> None:
        count = int(settings.WORLD_WIDTH * settings.WORLD_HEIGHT * settings.WILDLIFE_SPAWN_CHANCE)
        for _ in range(count):
            x = random.randint(0, self.bounds.width - settings.TILE_SIZE)
            y = random.randint(0, self.bounds.height - settings.TILE_SIZE)
            self.wildlife.append(Wildlife(pygame.Vector2(x, y)))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def tile_at_pixel(self, position: pygame.Vector2) -> str:
        tile_x = int(position.x // settings.TILE_SIZE)
        tile_y = int(position.y // settings.TILE_SIZE)
        if 0 <= tile_x < settings.WORLD_WIDTH and 0 <= tile_y < settings.WORLD_HEIGHT:
            return self.tiles[tile_y][tile_x]
        return "forest"

    def has_structure(self, structure_type: str) -> bool:
        return any(struct.structure_type == structure_type for struct in self.structures)

    def nearby_structures(self, rect: pygame.Rect, radius: float = 120) -> set[str]:
        structures: set[str] = set()
        center = pygame.Vector2(rect.center)
        for struct in self.structures:
            if center.distance_to(struct.position + pygame.Vector2(struct.rect().width / 2, struct.rect().height / 2)) <= radius:
                structures.add(struct.structure_type)
        return structures

    def place_structure(self, structure_type: str, position: pygame.Vector2) -> bool:
        if structure_type not in settings.STRUCTURE_RECIPES:
            return False
        aligned = pygame.Vector2(
            int(position.x // settings.TILE_SIZE) * settings.TILE_SIZE,
            int(position.y // settings.TILE_SIZE) * settings.TILE_SIZE,
        )
        if self.tile_at_pixel(aligned) in {"water", "bog"}:
            return False
        new_struct = Structure(aligned, structure_type)
        struct_rect = new_struct.rect()
        if any(struct.rect().colliderect(struct_rect) for struct in self.structures):
            return False
        self.structures.append(new_struct)
        return True

    def gather_at(self, player_rect: pygame.Rect) -> list[tuple[str, int]]:
        collected: list[tuple[str, int]] = []
        interaction_rect = player_rect.inflate(40, 40)
        for node in list(self.resource_nodes):
            if node.rect().colliderect(interaction_rect) and node.quantity > 0:
                node.quantity -= 1
                collected.append((node.resource_type, 1))
                if node.quantity <= 0:
                    node.respawn_timer = settings.RESOURCE_RESPAWN_TIME
        for structure in self.structures:
            if structure.storage and structure.rect().colliderect(interaction_rect):
                for resource, amount in list(structure.storage.items()):
                    if amount > 0:
                        collected.append((resource, amount))
                    structure.storage.pop(resource)
        if not collected:
            center = pygame.Vector2(player_rect.center)
            tile = self.tile_at_pixel(center)
            if tile in {"water", "bog"}:
                collected.append(("water", 1))
        return collected

    def hunt(self, player_rect: pygame.Rect) -> bool:
        strike_rect = player_rect.inflate(50, 50)
        for wildlife in list(self.wildlife):
            if wildlife.rect().colliderect(strike_rect):
                self.wildlife.remove(wildlife)
                return True
        return False

    def update(self, dt: float) -> None:
        self._update_weather(dt)
        for animal in self.wildlife:
            animal.update(dt, self.bounds)
        self._update_resources(dt)
        self._update_structures(dt)

    def _update_resources(self, dt: float) -> None:
        for node in list(self.resource_nodes):
            if node.quantity <= 0:
                node.respawn_timer -= dt
                if node.respawn_timer <= 0:
                    node.quantity = random.randint(1, 3)
            if node.quantity <= 0 and node.respawn_timer <= 0:
                self.resource_nodes.remove(node)

    def _update_structures(self, dt: float) -> None:
        for struct in self.structures:
            effects = settings.STRUCTURE_EFFECTS.get(struct.structure_type, {})
            struct.timer += dt
            if "supply_interval" in effects and struct.timer >= effects["supply_interval"]:
                struct.timer = 0
                resource = effects.get("resource")
                amount = effects.get("amount", 1)
                if resource:
                    struct.storage[resource] = struct.storage.get(resource, 0) + amount
            if "harvest_interval" in effects and struct.timer >= effects["harvest_interval"]:
                struct.timer = 0
                resource = effects.get("resource")
                amount = effects.get("amount", 1)
                if resource:
                    struct.storage[resource] = struct.storage.get(resource, 0) + amount

    def apply_structure_effects(self, player: "Player", dt: float) -> None:
        player_center = pygame.Vector2(player.rect().center)
        for struct in self.structures:
            effects = settings.STRUCTURE_EFFECTS.get(struct.structure_type, {})
            center = pygame.Vector2(struct.rect().center)
            distance = player_center.distance_to(center)
            if "warmth_radius" in effects and distance <= effects["warmth_radius"]:
                player.sanity = min(settings.MAX_SANITY, player.sanity + effects.get("sanity", 1) * dt)
            if "rest_radius" in effects and distance <= effects["rest_radius"]:
                stamina_bonus = effects.get("stamina", 0)
                sanity_bonus = effects.get("sanity_bonus", 0)
                player.rest(dt, stamina_bonus=stamina_bonus, sanity_bonus=sanity_bonus)

    def _update_weather(self, dt: float) -> None:
        self.weather_timer -= dt
        if self.weather_timer <= 0:
            self.weather = random.choice(settings.WEATHER_TYPES)
            self.weather_timer = random.uniform(*settings.WEATHER_DURATION)

    def render(self, surface: pygame.Surface, camera: Camera, time_of_day: float) -> None:
        surface.blit(self.surface, (0, 0), area=camera.screen_rect())
        offset = camera.offset
        view_rect = camera.screen_rect()
        for node in self.resource_nodes:
            node_rect = node.rect()
            if view_rect.colliderect(node_rect):
                draw_rect = node_rect.move(-offset.x, -offset.y)
                color = RESOURCE_COLORS.get(node.resource_type, settings.WHITE)
                pygame.draw.rect(surface, color, draw_rect)
        for struct in self.structures:
            struct_rect = struct.rect()
            if view_rect.colliderect(struct_rect):
                draw_rect = struct_rect.move(-offset.x, -offset.y)
                base_color = settings.STRUCTURE_COLORS.get(struct.structure_type, settings.WHITE)
                pygame.draw.rect(surface, base_color, draw_rect, border_radius=6)
                if struct.storage:
                    pygame.draw.rect(surface, settings.YELLOW, draw_rect, width=3)
        for animal in self.wildlife:
            animal_rect = animal.rect()
            if view_rect.colliderect(animal_rect):
                draw_rect = animal_rect.move(-offset.x, -offset.y)
                pygame.draw.rect(surface, settings.YELLOW, draw_rect, border_radius=8)
        self._draw_weather(surface)
        self.apply_lighting(surface, time_of_day)

    def _draw_weather(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        if self.weather == "rain":
            overlay.fill((40, 60, 80, 40))
            for _ in range(80):
                x = random.randint(0, surface.get_width())
                y = random.randint(0, surface.get_height())
                pygame.draw.line(overlay, settings.WATER_BLUE, (x, y), (x + 4, y + 12), 1)
        elif self.weather == "mist":
            overlay.fill((*settings.MIST_GRAY[:3], 35))
        surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    @staticmethod
    def apply_lighting(surface: pygame.Surface, time_of_day: float) -> None:
        cycle_position = (time_of_day % settings.DAY_LENGTH) / settings.DAY_LENGTH
        if cycle_position < 0.25:  # sunrise
            tint = settings.SKY_BLUE.lerp(settings.SUNSET_ORANGE, cycle_position / 0.25)
        elif cycle_position < 0.5:  # day
            tint = settings.SKY_BLUE
        elif cycle_position < 0.75:  # sunset
            tint = settings.SKY_BLUE.lerp(settings.NIGHT_BLUE, (cycle_position - 0.5) / 0.25)
        else:  # night
            tint = settings.NIGHT_BLUE
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*tint[:3], 50))
        surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .player import Player
