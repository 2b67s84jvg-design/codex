from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .constants import CARE_DECAY_PER_SECOND, RESOURCE_TYPES, STAT_MAX


@dataclass
class HybridCombo:
    with_id: str
    result: str
    hybrid_elements: List[str]
    base_chance: float


@dataclass
class BeastTemplate:
    id: str
    name: str
    element: List[str]
    rarity: str
    favorite_foods: List[str]
    signature_trait: str
    work_proficiency: str
    hybrid_combos: Dict[str, HybridCombo] = field(default_factory=dict)


@dataclass
class BeastInstance:
    template: BeastTemplate
    nickname: Optional[str] = None
    hunger: float = STAT_MAX
    thirst: float = STAT_MAX
    mood: float = STAT_MAX
    energy: float = STAT_MAX
    level: int = 1
    experience: float = 0.0
    assigned_task: Optional[str] = None
    task_timer: float = 0.0
    breeding_partner: Optional[str] = None
    breeding_timer: float = 0.0
    egg_timer: float = 0.0
    is_egg: bool = False
    egg_origin: Optional[List[str]] = None

    def update_needs(self, dt: float) -> None:
        if self.is_egg:
            self.egg_timer = max(0.0, self.egg_timer - dt)
            return
        self.hunger = max(0.0, self.hunger - CARE_DECAY_PER_SECOND["hunger"] * dt)
        self.thirst = max(0.0, self.thirst - CARE_DECAY_PER_SECOND["thirst"] * dt)
        self.mood = max(0.0, self.mood - CARE_DECAY_PER_SECOND["mood"] * dt)
        self.energy = max(0.0, self.energy - CARE_DECAY_PER_SECOND["energy"] * dt)

    def feed(self) -> None:
        self.hunger = min(STAT_MAX, self.hunger + 35)
        self.mood = min(STAT_MAX, self.mood + 10)

    def hydrate(self) -> None:
        self.thirst = min(STAT_MAX, self.thirst + 35)

    def play(self) -> None:
        if self.energy >= 10:
            self.mood = min(STAT_MAX, self.mood + 25)
            self.energy = max(0.0, self.energy - 8)

    def rest(self) -> None:
        self.energy = min(STAT_MAX, self.energy + 30)

    def assign_task(self, task: Optional[str], duration: float) -> None:
        self.assigned_task = task
        self.task_timer = duration
        if task:
            self.mood = max(0.0, self.mood - 5)

    def update_task(self, dt: float) -> Optional[str]:
        if not self.assigned_task:
            return None
        self.task_timer -= dt
        if self.task_timer <= 0:
            finished_task = self.assigned_task
            self.assigned_task = None
            self.task_timer = 0
            self.experience += 15
            return finished_task
        return None

    def start_breeding(self, partner_id: str, duration: float) -> None:
        self.breeding_partner = partner_id
        self.breeding_timer = duration

    def update_breeding(self, dt: float) -> bool:
        if not self.breeding_partner:
            return False
        self.breeding_timer -= dt
        if self.breeding_timer <= 0:
            self.breeding_partner = None
            self.breeding_timer = 0
            return True
        return False

    def start_egg(self, hatch_time: float, origin: List[str]) -> None:
        self.is_egg = True
        self.egg_timer = hatch_time
        self.egg_origin = origin

    def hatch(self, template: BeastTemplate) -> None:
        self.is_egg = False
        self.egg_timer = 0
        self.template = template
        self.nickname = template.name
        self.hunger = STAT_MAX
        self.thirst = STAT_MAX
        self.mood = STAT_MAX
        self.energy = STAT_MAX
        self.egg_origin = None


class BeastCatalog:
    def __init__(self, data_path: Path) -> None:
        with data_path.open("r", encoding="utf-8") as f:
            raw_data = json.load(f)
        self.templates: Dict[str, BeastTemplate] = {}
        for entry in raw_data:
            combos = {c["with"]: HybridCombo(
                with_id=c["with"],
                result=c["result"],
                hybrid_elements=c.get("hybridElements", []),
                base_chance=c.get("baseChance", 0.1),
            ) for c in entry.get("hybridCombos", [])}
            template = BeastTemplate(
                id=entry["id"],
                name=entry["name"],
                element=entry.get("element", []),
                rarity=entry.get("rarity", "Common"),
                favorite_foods=entry.get("favoriteFoods", []),
                signature_trait=entry.get("signatureTrait", ""),
                work_proficiency=entry.get("workProficiency", ""),
                hybrid_combos=combos,
            )
            self.templates[template.id] = template

        self.template_list = list(self.templates.values())

    def get_template(self, beast_id: str) -> BeastTemplate:
        return self.templates[beast_id]

    def random_template(self) -> BeastTemplate:
        return random.choice(self.template_list)

    def breed(self, parent_a: BeastTemplate, parent_b: BeastTemplate) -> BeastTemplate:
        combo = parent_a.hybrid_combos.get(parent_b.id)
        reverse_combo = parent_b.hybrid_combos.get(parent_a.id)
        combos = [c for c in [combo, reverse_combo] if c]
        if combos:
            combo_choice = random.choice(combos)
            if random.random() < combo_choice.base_chance:
                return self.templates.get(combo_choice.result, random.choice(self.template_list))
        return random.choice([parent_a, parent_b, self.random_template()])


def create_initial_beast(template: BeastTemplate) -> BeastInstance:
    return BeastInstance(template=template, nickname=template.name)


def create_egg(origin_ids: List[str], hatch_time: float) -> BeastInstance:
    placeholder_template = BeastTemplate(
        id="mystery_egg",
        name="Mystery Egg",
        element=["Unknown"],
        rarity="Unknown",
        favorite_foods=[],
        signature_trait="Dormant",
        work_proficiency="Incubating",
        hybrid_combos={},
    )
    beast = BeastInstance(template=placeholder_template)
    beast.start_egg(hatch_time, origin_ids)
    return beast


def reward_for_task(task: str) -> Dict[str, int]:
    if task == "forage":
        return {"herbs": random.randint(3, 7)}
    if task == "gather":
        return {"crystal": random.randint(2, 4), "stardust": random.randint(1, 3)}
    if task == "scout":
        return {"essence": random.randint(2, 5), "stardust": random.randint(1, 2)}
    return {}


def level_reward(beast: BeastInstance) -> Dict[str, int]:
    level = beast.level
    return {resource: random.randint(0, level) for resource in RESOURCE_TYPES}


def gain_experience(beast: BeastInstance, amount: float) -> bool:
    beast.experience += amount
    leveled = False
    while beast.experience >= 100:
        beast.level += 1
        beast.experience -= 100
        leveled = True
    return leveled
