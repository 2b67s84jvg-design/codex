from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from game.base import BUILDINGS, BaseState
from game.beasts import BeastCatalog, BeastInstance
from game.combat import CombatEngine, CombatParticipant
from game.constants import (
    ACCENT,
    BLACK,
    DARK_GREY,
    DEFAULT_FONT,
    FPS,
    LARGE_FONT,
    LIGHT_GREY,
    COMBAT_ACTIONS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SUCCESS,
    TITLE_FONT,
    WARNING,
)
from game.states import Screen
from game.ui import Button, draw_panel, draw_text


def load_catalog() -> BeastCatalog:
    data_path = Path(__file__).parent / "data" / "beasts.json"
    if not data_path.exists():
        data_path = Path.cwd() / "data" / "beasts.json"
    return BeastCatalog(data_path)


class ScrollList:
    def __init__(self, items: List, item_height: int, rect: pygame.Rect):
        self.items = items
        self.item_height = item_height
        self.rect = rect
        self.offset = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEWHEEL:
            max_offset = max(0, len(self.items) * self.item_height - self.rect.height)
            self.offset = max(0, min(max_offset, self.offset - event.y * self.item_height))

    def draw(self, surface: pygame.Surface, draw_item) -> None:
        clip = surface.get_clip()
        surface.set_clip(self.rect)
        y = self.rect.y - self.offset
        for index, item in enumerate(self.items):
            item_rect = pygame.Rect(self.rect.x, y, self.rect.width, self.item_height)
            draw_item(surface, index, item, item_rect)
            y += self.item_height
        surface.set_clip(clip)


class SpellboundGame:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Spellbound Sanctuary")
        self.clock = pygame.time.Clock()
        self.catalog = load_catalog()
        self.base_state = BaseState(self.catalog)
        self.game_state = Screen.TITLE
        self.selected_beast: Optional[BeastInstance] = None
        self.title_buttons: List[Button] = []
        self.selection_scroll: Optional[ScrollList] = None
        self.base_buttons: List[Button] = []
        self.care_buttons: List[Button] = []
        self.task_buttons: List[Button] = []
        self.action_message: str = "Welcome to Spellbound Sanctuary!"
        self.combat_engine = CombatEngine([], [template for template in self.catalog.template_list])
        self.combat_player: Optional[CombatParticipant] = None
        self.combat_enemy: Optional[CombatParticipant] = None
        self.combat_buttons: List[Button] = []
        self.turn_log: List[str] = []
        self.building_scroll: Optional[ScrollList] = None
        self.breeding_selection: List[BeastInstance] = []
        self.caretaker_options: List[Tuple[str, str]] = [
            ("Arcanist Rowan", "Man"),
            ("Seeress Lyra", "Woman"),
        ]
        self.caretaker_index: int = 0
        self._init_title_buttons()

    def _init_title_buttons(self) -> None:
        start_button = Button(
            rect=pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2, 240, 50),
            label="Start",
            callback=self._enter_selection,
        )
        self.title_buttons = [start_button]

    def _enter_selection(self) -> None:
        self.game_state = Screen.SELECTION
        self.selection_scroll = ScrollList(self.catalog.template_list, 70, pygame.Rect(100, 160, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 260))

    def _start_with_template(self, template_index: int) -> None:
        template = self.catalog.template_list[template_index]
        beast = self.base_state.add_initial_beast(template)
        self.selected_beast = beast
        self.game_state = Screen.BASE
        self._create_base_buttons()
        self.action_message = f"Bonded with {template.name}!"

    def _start_with_random_egg(self) -> None:
        template = self.catalog.random_template()
        beast = self.base_state.add_initial_beast(template)
        beast.nickname = "Mysterious Hatchling"
        beast.hunger = 60
        beast.thirst = 60
        beast.mood = 80
        beast.energy = 80
        self.selected_beast = beast
        self.game_state = Screen.BASE
        self._create_base_buttons()
        self.action_message = "A mysterious egg hatched into a surprise companion!"

    def _create_base_buttons(self) -> None:
        self.base_buttons = [
            Button(pygame.Rect(1040, 40, 200, 40), "Buildings", self._enter_building),
            Button(pygame.Rect(1040, 90, 200, 40), "Breeding", self._enter_breeding),
            Button(pygame.Rect(1040, 140, 200, 40), "Combat", self._enter_combat_select),
            Button(pygame.Rect(1040, 190, 200, 40), "Invite Beast", self._adopt_beast),
        ]
        care_actions = [
            ("Feed", "feed"),
            ("Hydrate", "hydrate"),
            ("Play", "play"),
            ("Rest", "rest"),
        ]
        self.care_buttons = []
        for i, (label, action) in enumerate(care_actions):
            rect = pygame.Rect(760, 260 + i * 50, 200, 40)
            self.care_buttons.append(Button(rect, label, lambda a=action: self._care_action(a)))
        tasks = [
            ("Forage", "forage"),
            ("Gather", "gather"),
            ("Scout", "scout"),
        ]
        self.task_buttons = []
        for i, (label, action) in enumerate(tasks):
            rect = pygame.Rect(980, 260 + i * 50, 200, 40)
            self.task_buttons.append(Button(rect, label, lambda a=action: self._assign_task(a)))
        self.task_buttons.append(Button(pygame.Rect(980, 260 + len(tasks) * 50, 200, 40), "Cancel Task", lambda: self._assign_task(None)))

    def _care_action(self, action: str) -> None:
        if not self.selected_beast:
            return
        self.base_state.care_action(self.selected_beast, action)
        self.action_message = f"{self.selected_beast.template.name} enjoyed {action}!"

    def _assign_task(self, task: Optional[str]) -> None:
        if not self.selected_beast:
            return
        if task and self.selected_beast.assigned_task:
            self.action_message = f"{self.selected_beast.template.name} is already busy."
            return
        self.base_state.assign_task(self.selected_beast, task)
        if task:
            self.action_message = f"Assigned {self.selected_beast.template.name} to {task}."
        else:
            self.action_message = f"{self.selected_beast.template.name} is now resting."

    def _adopt_beast(self) -> None:
        if len(self.base_state.beasts) >= self.base_state.max_capacity:
            self.action_message = "The sanctuary is at full capacity."
            return
        cost = {"stardust": 8, "essence": 5}
        if any(self.base_state.resources.get(res, 0) < amt for res, amt in cost.items()):
            self.action_message = "Need more stardust and essence to invite a beast."
            return
        for res, amt in cost.items():
            self.base_state.resources[res] -= amt
        template = self.catalog.random_template()
        beast = self.base_state.add_initial_beast(template)
        self.selected_beast = beast
        self.action_message = f"A wandering {template.name} joined your sanctuary!"

    def _enter_building(self) -> None:
        self.game_state = Screen.BUILDING
        building_items = list(BUILDINGS.items())
        self.building_scroll = ScrollList(building_items, 100, pygame.Rect(140, 140, SCREEN_WIDTH - 280, SCREEN_HEIGHT - 240))

    def _enter_breeding(self) -> None:
        if len(self.base_state.beasts) < 2:
            self.action_message = "You need at least two beasts to breed."
            return
        self.game_state = Screen.BREEDING
        self.breeding_selection = []

    def _enter_combat_select(self) -> None:
        if not self.base_state.beasts:
            self.action_message = "No beasts available for combat yet."
            return
        self.game_state = Screen.COMBAT_SELECT

    def _start_combat(self, beast: BeastInstance) -> None:
        self.combat_engine.roster = self.base_state.beasts
        player, enemy = self.combat_engine.start_encounter(beast)
        self.combat_player = player
        self.combat_enemy = enemy
        self.combat_buttons = []
        for i, action in enumerate(COMBAT_ACTIONS):
            rect = pygame.Rect(900, 260 + i * 60, 180, 50)
            self.combat_buttons.append(Button(rect, action, lambda a=action: self._perform_combat_turn(a)))
        self.turn_log = []
        self.game_state = Screen.COMBAT

    def _perform_combat_turn(self, action: str) -> None:
        if not self.combat_player or not self.combat_enemy:
            return
        self.combat_engine.execute_turn(self.combat_player, self.combat_enemy, action)
        self.turn_log = [f"{log.actor} uses {log.action} and {log.result}" for log in self.combat_engine.turn_log]
        if self.combat_enemy.current_health <= 0 or self.combat_player.current_health <= 0:
            result = self.combat_engine.conclude_battle(self.combat_player, self.combat_enemy)
            self.action_message = f"Combat {result['outcome']}!"
            self.game_state = Screen.BASE
            self._create_base_buttons()
            self.combat_player = None
            self.combat_enemy = None

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.game_state == Screen.TITLE:
                    self._handle_title_event(event)
                    for button in self.title_buttons:
                        button.handle_event(event)
                elif self.game_state == Screen.SELECTION:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._handle_selection_click(event.pos)
                    if self.selection_scroll:
                        self.selection_scroll.handle_event(event)
                elif self.game_state == Screen.BASE:
                    for button in self.base_buttons + self.care_buttons + self.task_buttons:
                        button.handle_event(event)
                    self._handle_beast_list_event(event)
                elif self.game_state == Screen.BUILDING:
                    self._handle_building_event(event)
                elif self.game_state == Screen.BREEDING:
                    self._handle_breeding_event(event)
                elif self.game_state == Screen.COMBAT_SELECT:
                    self._handle_combat_select(event)
                elif self.game_state == Screen.COMBAT:
                    for button in self.combat_buttons:
                        button.handle_event(event)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.game_state = Screen.BASE
                        self._create_base_buttons()
            if self.game_state == Screen.BASE:
                collected = self.base_state.update(dt)
                if any(amount > 0 for amount in collected.values()):
                    self.action_message = f"Gathered resources: {collected}"
            else:
                self.base_state.update(dt)
            self._render()

    def _handle_selection_click(self, pos: Tuple[int, int]) -> None:
        if not self.selection_scroll:
            return
        y = self.selection_scroll.rect.y - self.selection_scroll.offset
        for index, template in enumerate(self.catalog.template_list):
            item_rect = pygame.Rect(self.selection_scroll.rect.x, y, self.selection_scroll.rect.width, self.selection_scroll.item_height)
            if item_rect.collidepoint(pos):
                self._start_with_template(index)
                return
            y += self.selection_scroll.item_height
        random_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 80, 300, 50)
        if random_rect.collidepoint(pos):
            self._start_with_random_egg()

    def _handle_beast_list_event(self, event: pygame.event.Event) -> None:
        list_rect = pygame.Rect(40, 120, 300, SCREEN_HEIGHT - 200)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            y = list_rect.y
            for beast in self.base_state.beasts:
                beast_rect = pygame.Rect(list_rect.x, y, list_rect.width, 60)
                if beast_rect.collidepoint(event.pos):
                    self.selected_beast = beast
                    self.action_message = f"Selected {beast.template.name}."
                    return
                y += 70
        elif event.type == pygame.MOUSEWHEEL:
            pass

    def _handle_building_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = Screen.BASE
            self._create_base_buttons()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.building_scroll:
            y = self.building_scroll.rect.y - self.building_scroll.offset
            for name, building in self.building_scroll.items:
                item_rect = pygame.Rect(self.building_scroll.rect.x, y, self.building_scroll.rect.width, self.building_scroll.item_height)
                if item_rect.collidepoint(event.pos):
                    success = self.base_state.build_structure(name)
                    if success:
                        self.action_message = f"Built {name}!"
                    else:
                        self.action_message = f"Cannot build {name} yet."
                    self.game_state = Screen.BASE
                    self._create_base_buttons()
                    return
                y += self.building_scroll.item_height

    def _handle_breeding_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = Screen.BASE
            self._create_base_buttons()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            list_rect = pygame.Rect(100, 160, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 260)
            y = list_rect.y
            for beast in self.base_state.beasts:
                beast_rect = pygame.Rect(list_rect.x, y, list_rect.width, 60)
                if beast_rect.collidepoint(event.pos):
                    if beast not in self.breeding_selection:
                        self.breeding_selection.append(beast)
                        if len(self.breeding_selection) == 2:
                            egg = self.base_state.try_breed(self.breeding_selection[0], self.breeding_selection[1])
                            if egg:
                                self.action_message = "Breeding underway!"
                            else:
                                self.action_message = "No space for a new egg."
                            self.game_state = Screen.BASE
                            self._create_base_buttons()
                            self.breeding_selection = []
                    return
                y += 70

    def _handle_combat_select(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = Screen.BASE
            self._create_base_buttons()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            list_rect = pygame.Rect(100, 160, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 260)
            y = list_rect.y
            for beast in self.base_state.beasts:
                beast_rect = pygame.Rect(list_rect.x, y, list_rect.width, 60)
                if beast_rect.collidepoint(event.pos):
                    self._start_combat(beast)
                    return
                y += 70

    def _render(self) -> None:
        self.screen.fill(DARK_GREY)
        if self.game_state == Screen.TITLE:
            self._render_title()
        elif self.game_state == Screen.SELECTION:
            self._render_selection()
        elif self.game_state == Screen.BASE:
            self._render_base()
        elif self.game_state == Screen.BUILDING:
            self._render_buildings()
        elif self.game_state == Screen.BREEDING:
            self._render_breeding()
        elif self.game_state == Screen.COMBAT_SELECT:
            self._render_combat_select()
        elif self.game_state == Screen.COMBAT:
            self._render_combat()
        pygame.display.flip()

    def _render_title(self) -> None:
        draw_text(self.screen, "Spellbound Sanctuary", (SCREEN_WIDTH // 2 - 260, 200), ACCENT, TITLE_FONT)
        draw_text(self.screen, "Care for your magical beasts and build a thriving refuge!", (SCREEN_WIDTH // 2 - 320, 270), LIGHT_GREY)
        draw_text(self.screen, "Choose your caretaker avatar", (SCREEN_WIDTH // 2 - 180, 310), LIGHT_GREY)
        for idx, rect in enumerate(self._caretaker_rects()):
            active = idx == self.caretaker_index
            pygame.draw.rect(self.screen, ACCENT if active else LIGHT_GREY, rect, 0 if active else 2, border_radius=10)
            name, descriptor = self.caretaker_options[idx]
            draw_text(self.screen, name, (rect.x + 16, rect.y + 24), BLACK if active else LIGHT_GREY)
            draw_text(self.screen, descriptor, (rect.x + 16, rect.y + 56), BLACK if active else LIGHT_GREY)
        mouse_pos = pygame.mouse.get_pos()
        for button in self.title_buttons:
            button.draw(self.screen, mouse_pos)

    def _render_selection(self) -> None:
        draw_text(self.screen, "Choose your first companion or risk a mystery egg!", (180, 100), LIGHT_GREY, LARGE_FONT)
        if self.selection_scroll:
            def draw_item(surface, index, template, rect):
                pygame.draw.rect(surface, ACCENT if rect.collidepoint(pygame.mouse.get_pos()) else LIGHT_GREY, rect, 2)
                draw_text(surface, f"{template.name} ({', '.join(template.element)})", (rect.x + 16, rect.y + 10))
                draw_text(surface, f"Trait: {template.signature_trait}", (rect.x + 16, rect.y + 34), LIGHT_GREY)
            self.selection_scroll.draw(self.screen, draw_item)
        random_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 80, 300, 50)
        pygame.draw.rect(self.screen, ACCENT, random_rect, border_radius=8)
        draw_text(self.screen, "Adopt a Mystery Egg", (random_rect.x + 40, random_rect.y + 14), BLACK)

    def _render_base(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        draw_text(self.screen, "Sanctuary Base", (40, 40), ACCENT, LARGE_FONT)
        caretaker_name, descriptor = self.caretaker_options[self.caretaker_index]
        draw_text(self.screen, f"Caretaker: {caretaker_name} ({descriptor})", (360, 40), LIGHT_GREY)
        draw_text(self.screen, self.action_message, (40, 80), LIGHT_GREY)
        list_rect = pygame.Rect(40, 120, 300, SCREEN_HEIGHT - 200)
        draw_panel(self.screen, list_rect, "Beasts")
        y = list_rect.y + 40
        for beast in self.base_state.beasts:
            beast_rect = pygame.Rect(list_rect.x + 10, y, list_rect.width - 20, 50)
            pygame.draw.rect(self.screen, ACCENT if beast == self.selected_beast else LIGHT_GREY, beast_rect, 0 if beast == self.selected_beast else 2, border_radius=8)
            draw_text(self.screen, beast.template.name, (beast_rect.x + 10, beast_rect.y + 10), BLACK if beast == self.selected_beast else LIGHT_GREY)
            draw_text(self.screen, f"Lv {beast.level} • Task: {beast.assigned_task or 'Idle'}", (beast_rect.x + 10, beast_rect.y + 28), BLACK if beast == self.selected_beast else LIGHT_GREY)
            y += 60
        details_rect = pygame.Rect(360, 120, 360, SCREEN_HEIGHT - 200)
        draw_panel(self.screen, details_rect, "Details")
        if self.selected_beast:
            beast = self.selected_beast
            draw_text(self.screen, beast.template.name, (details_rect.x + 16, details_rect.y + 40), ACCENT, LARGE_FONT)
            draw_text(self.screen, f"Element: {', '.join(beast.template.element)}", (details_rect.x + 16, details_rect.y + 90))
            draw_text(self.screen, f"Trait: {beast.template.signature_trait}", (details_rect.x + 16, details_rect.y + 120))
            draw_text(self.screen, f"Rarity: {beast.template.rarity}", (details_rect.x + 16, details_rect.y + 150))
            stats = [
                ("Hunger", beast.hunger),
                ("Thirst", beast.thirst),
                ("Mood", beast.mood),
                ("Energy", beast.energy),
            ]
            for i, (label, value) in enumerate(stats):
                bar_rect = pygame.Rect(details_rect.x + 16, details_rect.y + 200 + i * 40, 220, 20)
                pygame.draw.rect(self.screen, LIGHT_GREY, bar_rect, 2, border_radius=4)
                fill = pygame.Rect(bar_rect.x + 2, bar_rect.y + 2, int((bar_rect.width - 4) * (value / 100)), bar_rect.height - 4)
                pygame.draw.rect(self.screen, SUCCESS if value >= 40 else WARNING, fill, border_radius=4)
                draw_text(self.screen, f"{label}: {int(value)}", (bar_rect.x, bar_rect.y - 22))
            draw_text(self.screen, f"XP: {int(beast.experience)}/100 (Lv {beast.level})", (details_rect.x + 16, details_rect.y + 360))
            if beast.assigned_task:
                draw_text(self.screen, f"Task time left: {int(beast.task_timer)}", (details_rect.x + 16, details_rect.y + 390))
            if beast.breeding_partner:
                draw_text(self.screen, f"Breeding cooldown: {int(beast.breeding_timer)}", (details_rect.x + 16, details_rect.y + 420))
        resources_rect = pygame.Rect(740, 120, 520, 120)
        draw_panel(self.screen, resources_rect, "Resources")
        rx = resources_rect.x + 16
        ry = resources_rect.y + 40
        for resource, amount in self.base_state.resources.items():
            draw_text(self.screen, f"{resource.title()}: {amount}", (rx, ry))
            ry += 24
        draw_text(self.screen, f"Beasts: {len(self.base_state.beasts)} / {self.base_state.max_capacity}", (resources_rect.x + 280, resources_rect.y + 40))
        draw_text(self.screen, "Structures: " + (", ".join(self.base_state.buildings) if self.base_state.buildings else "None"), (resources_rect.x + 280, resources_rect.y + 70), LIGHT_GREY)
        for button in self.base_buttons + self.care_buttons + self.task_buttons:
            button.draw(self.screen, mouse_pos)
        eggs_rect = pygame.Rect(740, 420, 520, 200)
        draw_panel(self.screen, eggs_rect, "Incubation")
        ey = eggs_rect.y + 40
        if self.base_state.eggs:
            for egg in self.base_state.eggs:
                draw_text(self.screen, f"Egg ({egg.parent_ids[0]} x {egg.parent_ids[1]}) - {int(egg.timer)}s", (eggs_rect.x + 16, ey), LIGHT_GREY)
                ey += 24
        else:
            draw_text(self.screen, "No eggs incubating", (eggs_rect.x + 16, ey), LIGHT_GREY)

    def _render_buildings(self) -> None:
        draw_text(self.screen, "Construct Buildings", (200, 80), ACCENT, LARGE_FONT)
        draw_text(self.screen, "Click a structure to build it. Press Esc to return.", (200, 120), LIGHT_GREY)
        if self.building_scroll:
            def draw_item(surface, index, item, rect):
                name, building = item
                pygame.draw.rect(surface, ACCENT if rect.collidepoint(pygame.mouse.get_pos()) else LIGHT_GREY, rect, 2)
                draw_text(surface, name, (rect.x + 16, rect.y + 10))
                draw_text(surface, building.description, (rect.x + 16, rect.y + 36), LIGHT_GREY)
                cost_text = ", ".join(f"{res}: {cost}" for res, cost in building.cost.items())
                draw_text(surface, f"Cost: {cost_text}", (rect.x + 16, rect.y + 60), LIGHT_GREY)
            items = list(BUILDINGS.items())
            if self.building_scroll:
                self.building_scroll.items = items
                self.building_scroll.draw(self.screen, draw_item)

    def _render_breeding(self) -> None:
        draw_text(self.screen, "Select two beasts to begin breeding. Press Esc to cancel.", (120, 80), ACCENT, LARGE_FONT)
        list_rect = pygame.Rect(100, 160, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 260)
        draw_panel(self.screen, list_rect)
        y = list_rect.y + 20
        for beast in self.base_state.beasts:
            beast_rect = pygame.Rect(list_rect.x + 20, y, list_rect.width - 40, 60)
            color = ACCENT if beast in self.breeding_selection else LIGHT_GREY
            pygame.draw.rect(self.screen, color, beast_rect, 2, border_radius=8)
            draw_text(self.screen, f"{beast.template.name} (Lv {beast.level})", (beast_rect.x + 16, beast_rect.y + 18))
            y += 70

    def _render_combat_select(self) -> None:
        draw_text(self.screen, "Choose a beast to send into combat. Esc to cancel.", (160, 80), ACCENT, LARGE_FONT)
        list_rect = pygame.Rect(100, 160, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 260)
        draw_panel(self.screen, list_rect)
        y = list_rect.y + 20
        for beast in self.base_state.beasts:
            beast_rect = pygame.Rect(list_rect.x + 20, y, list_rect.width - 40, 60)
            pygame.draw.rect(self.screen, ACCENT if beast == self.selected_beast else LIGHT_GREY, beast_rect, 2, border_radius=8)
            draw_text(self.screen, f"{beast.template.name} (Lv {beast.level})", (beast_rect.x + 16, beast_rect.y + 18))
            y += 70

    def _render_combat(self) -> None:
        if not self.combat_player or not self.combat_enemy:
            return
        draw_text(self.screen, "Turn-Based Combat", (180, 60), ACCENT, LARGE_FONT)
        player = self.combat_player
        enemy = self.combat_enemy
        draw_panel(self.screen, pygame.Rect(140, 140, 300, 200), player.beast.template.name)
        draw_text(self.screen, f"HP: {player.current_health}/{player.stats.health}", (160, 200))
        draw_text(self.screen, f"ATK: {player.stats.attack} FOC: {player.stats.focus}", (160, 240))
        draw_text(self.screen, f"DEF: {player.stats.defense}", (160, 280))
        draw_panel(self.screen, pygame.Rect(640, 140, 300, 200), enemy.beast.template.name)
        draw_text(self.screen, f"HP: {enemy.current_health}/{enemy.stats.health}", (660, 200))
        draw_text(self.screen, f"ATK: {enemy.stats.attack} FOC: {enemy.stats.focus}", (660, 240))
        draw_text(self.screen, f"DEF: {enemy.stats.defense}", (660, 280))
        for button in self.combat_buttons:
            button.draw(self.screen, pygame.mouse.get_pos())
        log_rect = pygame.Rect(140, 380, 800, 200)
        draw_panel(self.screen, log_rect, "Battle Log")
        y = log_rect.y + 40
        for line in self.turn_log[-6:]:
            draw_text(self.screen, line, (log_rect.x + 16, y), LIGHT_GREY)
            y += 28

    def _caretaker_rects(self) -> List[pygame.Rect]:
        base_x = SCREEN_WIDTH // 2 - 260
        y = 340
        rects = []
        for idx in range(len(self.caretaker_options)):
            rects.append(pygame.Rect(base_x + idx * 270, y, 240, 110))
        return rects

    def _handle_title_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, rect in enumerate(self._caretaker_rects()):
                if rect.collidepoint(event.pos):
                    self.caretaker_index = idx


def main() -> None:
    game = SpellboundGame()
    game.run()


if __name__ == "__main__":
    main()
