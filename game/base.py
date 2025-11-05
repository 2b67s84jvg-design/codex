from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .beasts import (
    BeastCatalog,
    BeastInstance,
    BeastTemplate,
    create_egg,
    create_initial_beast,
    gain_experience,
    level_reward,
    reward_for_task,
)
from .constants import BREEDING_DURATION, EGG_HATCH_TIME, RESOURCE_TYPES, STAT_MAX, TASK_DURATION


@dataclass
class Building:
    name: str
    cost: Dict[str, int]
    capacity_bonus: int = 0
    description: str = ""


BUILDINGS: Dict[str, Building] = {
    "Starlight Garden": Building(
        name="Starlight Garden",
        cost={"herbs": 12, "stardust": 6},
        description="Improves forage yields.",
    ),
    "Crystal Loom": Building(
        name="Crystal Loom",
        cost={"crystal": 10, "essence": 4},
        description="Unlocks advanced crafting tasks.",
    ),
    "Moonwell": Building(
        name="Moonwell",
        cost={"essence": 8, "stardust": 4},
        description="Slows thirst decay for all beasts.",
    ),
    "Sanctum Roost": Building(
        name="Sanctum Roost",
        cost={"stardust": 12, "crystal": 6},
        capacity_bonus=6,
        description="Expands beast capacity by 6.",
    ),
    "Celestial Conservatory": Building(
        name="Celestial Conservatory",
        cost={"essence": 14, "crystal": 10},
        capacity_bonus=8,
        description="Sanctuary wing for hybrid research adding beast slots.",
    ),
    "Mythic Archives": Building(
        name="Mythic Archives",
        cost={"stardust": 10, "herbs": 16},
        capacity_bonus=5,
        description="Library habitats that support additional scholars.",
    ),
    "Dreamer's Atrium": Building(
        name="Dreamer's Atrium",
        cost={"essence": 18, "stardust": 12},
        capacity_bonus=7,
        description="Meditation halls increasing harmony and beast space.",
    ),
    "Arcane Workshop": Building(
        name="Arcane Workshop",
        cost={"crystal": 8, "essence": 6},
        description="Unlocks new combat charms.",
    ),
}


@dataclass
class EggIncubation:
    parent_ids: Tuple[str, str]
    timer: float
    placeholder: BeastInstance


@dataclass
class BaseState:
    catalog: BeastCatalog
    beasts: List[BeastInstance] = field(default_factory=list)
    eggs: List[EggIncubation] = field(default_factory=list)
    resources: Dict[str, int] = field(default_factory=lambda: {resource: 10 for resource in RESOURCE_TYPES})
    buildings: List[str] = field(default_factory=list)
    capacity: int = 6

    def add_initial_beast(self, template: BeastTemplate) -> BeastInstance:
        beast = create_initial_beast(template)
        self.beasts.append(beast)
        return beast

    def can_add_beast(self) -> bool:
        return len(self.beasts) + len(self.eggs) < self.max_capacity

    @property
    def max_capacity(self) -> int:
        bonus = sum(BUILDINGS[b].capacity_bonus for b in self.buildings if b in BUILDINGS)
        return min(30, self.capacity + bonus)

    def update(self, dt: float) -> Dict[str, int]:
        collected: Dict[str, int] = {resource: 0 for resource in RESOURCE_TYPES}
        for beast in self.beasts:
            beast.update_needs(dt)
            if beast.breeding_partner:
                beast.update_breeding(dt)
            if beast.assigned_task:
                finished_task = beast.update_task(dt)
                if finished_task:
                    rewards = reward_for_task(finished_task)
                    for resource, amount in rewards.items():
                        collected[resource] += amount
                    if gain_experience(beast, 10):
                        bonus = level_reward(beast)
                        for resource, amount in bonus.items():
                            collected[resource] += amount
        for egg in list(self.eggs):
            egg.timer -= dt
            if egg.timer <= 0:
                template = self.catalog.breed(
                    self.catalog.get_template(egg.parent_ids[0]),
                    self.catalog.get_template(egg.parent_ids[1]),
                )
                egg.placeholder.hatch(template)
                self.eggs.remove(egg)
                if len(self.beasts) < self.max_capacity:
                    self.beasts.append(egg.placeholder)
        for resource, amount in collected.items():
            self.resources[resource] += amount
        return collected

    def hatch_egg(self, egg: EggIncubation, template: BeastTemplate) -> None:
        egg.placeholder.hatch(template)
        self.eggs.remove(egg)
        if len(self.beasts) < self.max_capacity:
            self.beasts.append(egg.placeholder)

    def assign_task(self, beast: BeastInstance, task: Optional[str]) -> None:
        if task is None:
            beast.assign_task(None, 0)
            return
        duration = TASK_DURATION.get(task, 20)
        beast.assign_task(task, duration)

    def try_breed(self, beast_a: BeastInstance, beast_b: BeastInstance) -> Optional[EggIncubation]:
        if not self.can_add_beast():
            return None
        if beast_a.breeding_partner or beast_b.breeding_partner:
            return None
        if beast_a.is_egg or beast_b.is_egg:
            return None
        beast_a.start_breeding(beast_b.template.id, BREEDING_DURATION)
        beast_b.start_breeding(beast_a.template.id, BREEDING_DURATION)
        placeholder = create_egg([beast_a.template.id, beast_b.template.id], EGG_HATCH_TIME)
        egg = EggIncubation(parent_ids=(beast_a.template.id, beast_b.template.id), timer=EGG_HATCH_TIME, placeholder=placeholder)
        self.eggs.append(egg)
        return egg

    def grant_resources(self, rewards: Dict[str, int]) -> None:
        for resource, amount in rewards.items():
            self.resources[resource] = self.resources.get(resource, 0) + amount

    def build_structure(self, name: str) -> bool:
        building = BUILDINGS.get(name)
        if not building:
            return False
        if name in self.buildings:
            return False
        if any(self.resources.get(res, 0) < cost for res, cost in building.cost.items()):
            return False
        for res, cost in building.cost.items():
            self.resources[res] -= cost
        self.buildings.append(name)
        return True

    def care_action(self, beast: BeastInstance, action: str) -> None:
        if action == "feed":
            beast.feed()
        elif action == "hydrate":
            beast.hydrate()
        elif action == "play":
            beast.play()
        elif action == "rest":
            beast.rest()

    def revive_needs(self, beast: BeastInstance) -> None:
        beast.hunger = STAT_MAX
        beast.thirst = STAT_MAX
        beast.mood = STAT_MAX
        beast.energy = STAT_MAX
