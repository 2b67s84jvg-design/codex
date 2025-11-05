"""Entry point for the Amazon survival RPG prototype."""
from __future__ import annotations

import sys
from collections import deque
from itertools import cycle

import pygame

from game import settings
from game.camera import Camera, world_pixel_size
from game.player import Player
from game.quests import QuestContext, default_quests
from game.ui import HUD, PauseOverlay
from game.world import World


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Sunheart Reliquary - Prototype")
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.hud = HUD(self.font, self.small_font)
        self.pause_overlay = PauseOverlay(pygame.font.SysFont("arial", 36, bold=True))
        self.world = World()
        world_width, world_height = world_pixel_size()
        self.camera = Camera(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, world_width, world_height)
        spawn_position = self._find_spawn_point()
        self.player = Player(position=spawn_position)
        self.messages: deque[str] = deque(maxlen=12)
        self.time_of_day = 0.0
        self.show_inventory = False
        self.show_crafting = False
        self.paused = False
        self.build_mode = False
        self.structure_names = list(settings.STRUCTURE_RECIPES.keys())
        self.selected_structure_index = 0
        self.quest_log = default_quests()
        self.hint_cycle = cycle(
            [
                "[E] Gather  [F] Eat  [G] Drink  [H] Heal",
                "[Space] Hunt  [C] Toggle crafting  [Tab] Inventory",
                "[B] Build mode  [Esc] Pause",
            ]
        )
        self.current_hint = next(self.hint_cycle)
        self.hint_timer = 0.0

    def run(self) -> None:
        while True:
            dt = self.clock.tick(settings.FPS) / 1000
            self.handle_events()
            if not self.paused:
                self.update(dt)
            self.render(paused=self.paused)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == settings.PAUSE_KEY:
                    self.paused = not self.paused
                if event.key == settings.INVENTORY_KEY:
                    self.show_inventory = not self.show_inventory
                if event.key == settings.CRAFT_KEY:
                    self.show_crafting = not self.show_crafting
                if event.key == settings.BUILD_KEY:
                    self.build_mode = not self.build_mode
                if event.key == settings.INTERACT_KEY:
                    self.gather_resources()
                if event.key == settings.ATTACK_KEY:
                    self.attempt_hunt()
                if event.key == pygame.K_f:
                    self.consume_resource("food")
                if event.key == pygame.K_g:
                    self.consume_resource("water")
                if event.key == pygame.K_h:
                    self.consume_resource("bandage")
                if event.key == pygame.K_j:
                    self.consume_resource("herb")
                if event.key == pygame.K_k:
                    self.consume_resource("cooked_meat")
                if event.key == pygame.K_1:
                    self.attempt_craft(0)
                if event.key == pygame.K_2:
                    self.attempt_craft(1)
                if event.key == pygame.K_3:
                    self.attempt_craft(2)
                if event.key == pygame.K_4:
                    self.attempt_craft(3)
                if event.key == pygame.K_5:
                    self.attempt_craft(4)
                if event.key == pygame.K_6:
                    self.attempt_craft(5)
                if self.build_mode:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.selected_structure_index = (self.selected_structure_index - 1) % len(self.structure_names)
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.selected_structure_index = (self.selected_structure_index + 1) % len(self.structure_names)
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.attempt_place_structure()

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.player.move(dt, keys, self.world.bounds)
        self.player.update_vitals(dt, self.world.weather)
        self.world.update(dt)
        self.world.apply_structure_effects(self.player, dt)
        self.camera.update(self.player.rect())
        self.time_of_day += dt
        self.hint_timer += dt
        if self.hint_timer >= 12:
            self.current_hint = next(self.hint_cycle)
            self.hint_timer = 0
        ctx = QuestContext(self.player, self.world)
        for message in self.quest_log.update(ctx):
            self.messages.append(message)
        if self.player.health <= 0:
            self.messages.append("You succumbed to the jungle...")
            self.paused = True

    def render(self, paused: bool = False) -> None:
        self.world.render(self.screen, self.camera, self.time_of_day)
        self.draw_player()
        self.draw_hud()
        if paused:
            self.pause_overlay.draw(self.screen)
        pygame.display.flip()

    def draw_player(self) -> None:
        offset = self.camera.offset
        player_rect = self.player.rect().move(-offset.x, -offset.y)
        pygame.draw.rect(self.screen, settings.WHITE, player_rect, border_radius=6)
        center = player_rect.center
        indicator = (
            center[0] + int(self.player.facing.x * 20),
            center[1] + int(self.player.facing.y * 20),
        )
        pygame.draw.line(self.screen, settings.YELLOW, center, indicator, 3)

    def draw_hud(self) -> None:
        self.hud.draw_bar(self.screen, "Health", self.player.health, settings.MAX_HEALTH, settings.RED, (20, 20))
        self.hud.draw_bar(self.screen, "Hunger", self.player.hunger, settings.MAX_HUNGER, settings.YELLOW, (20, 70))
        self.hud.draw_bar(self.screen, "Thirst", self.player.thirst, settings.MAX_THIRST, settings.SKY_BLUE, (20, 120))
        self.hud.draw_bar(self.screen, "Stamina", self.player.stamina, settings.MAX_STAMINA, settings.WHITE, (20, 170))
        self.hud.draw_bar(self.screen, "Sanity", self.player.sanity, settings.MAX_SANITY, settings.SUNSET_ORANGE, (20, 220))
        day = int(self.time_of_day // settings.DAY_LENGTH) + 1
        time_text = self.small_font.render(f"Day {day}", True, settings.WHITE)
        self.screen.blit(time_text, (settings.SCREEN_WIDTH - 180, 20))
        hint_text = self.small_font.render(self.current_hint, True, settings.WHITE)
        self.screen.blit(hint_text, (20, settings.SCREEN_HEIGHT - 200))
        self.hud.draw_weather(self.screen, self.world.weather, self.world.weather_timer)
        self.hud.draw_messages(self.screen, list(self.messages))
        self.hud.draw_quest_log(self.screen, self.quest_log.objectives())
        if self.show_inventory:
            self.hud.draw_inventory(self.screen, self.player.inventory)
        if self.show_crafting:
            self.hud.draw_crafting(self.screen, settings.CRAFTING_RECIPES, self.player.inventory)
        if self.build_mode:
            self.hud.draw_build_panel(self.screen, self.structure_names, self.selected_structure_index)

    def gather_resources(self) -> None:
        collected = self.world.gather_at(self.player.rect())
        if collected:
            for resource, amount in collected:
                self.player.add_item(resource, amount)
                self.messages.append(f"Gathered {resource} x{amount}")
        else:
            self.messages.append("Nothing to gather here")

    def consume_resource(self, resource: str) -> None:
        if self.player.consume(resource):
            self.messages.append(f"Consumed {resource}")
        else:
            self.messages.append(f"No {resource} to consume")

    def attempt_craft(self, index: int) -> None:
        recipe_names = list(settings.CRAFTING_RECIPES.keys())
        if index >= len(recipe_names):
            return
        recipe_name = recipe_names[index]
        nearby = self.world.nearby_structures(self.player.rect())
        if self.player.craft(recipe_name, nearby):
            self.messages.append(f"Crafted {recipe_name}")
        else:
            if recipe_name == "cooked_meat" and "campfire" not in nearby:
                self.messages.append("Need a campfire to cook meat")
            else:
                self.messages.append(f"Missing ingredients for {recipe_name}")

    def attempt_place_structure(self) -> None:
        structure_name = self.structure_names[self.selected_structure_index]
        cost = settings.STRUCTURE_RECIPES[structure_name]
        if not self.player.has_resources(cost):
            self.messages.append("Not enough resources to build")
            return
        placement = pygame.Vector2(self.player.rect().center) + self.player.facing * settings.TILE_SIZE
        if self.world.place_structure(structure_name, placement):
            for resource, amount in cost.items():
                self.player.inventory[resource] -= amount
            self.messages.append(f"Built {structure_name}")
        else:
            self.messages.append("Cannot place structure here")

    def attempt_hunt(self) -> None:
        if self.world.hunt(self.player.rect()):
            self.player.add_item("raw_meat", 1)
            self.messages.append("Hunted wildlife: raw meat added")
        else:
            self.messages.append("Nothing to hunt nearby")

    def _find_spawn_point(self) -> pygame.Vector2:
        world_width, world_height = world_pixel_size()
        center = pygame.Vector2(world_width // 2, world_height // 2)
        if self.world.tile_at_pixel(center) not in {"water", "bog"}:
            return center
        search_steps = [
            pygame.Vector2(dx * settings.TILE_SIZE, dy * settings.TILE_SIZE)
            for dx in range(-5, 6)
            for dy in range(-5, 6)
        ]
        for offset in search_steps:
            candidate = center + offset
            if self.world.bounds.collidepoint(candidate.x, candidate.y) and self.world.tile_at_pixel(candidate) not in {
                "water",
                "bog",
            }:
                return candidate
        return center


if __name__ == "__main__":
    Game().run()
