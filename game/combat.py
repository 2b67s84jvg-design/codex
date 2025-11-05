from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple

from .beasts import BeastInstance, BeastTemplate, gain_experience
from .constants import COMBAT_ACTIONS


@dataclass
class CombatStats:
    health: int
    attack: int
    focus: int
    defense: int


@dataclass
class CombatParticipant:
    beast: BeastInstance
    stats: CombatStats
    current_health: int
    guard_bonus: int = 0

    @classmethod
    def from_beast(cls, beast: BeastInstance) -> "CombatParticipant":
        template = beast.template
        rarity_mod = {"Common": 1, "Uncommon": 2, "Rare": 3, "Legendary": 4}.get(template.rarity, 1)
        base = 60 + beast.level * 10 + rarity_mod * 15
        attack = 10 + beast.level * 2 + rarity_mod * 3
        focus = 8 + beast.level * 2 + rarity_mod * 2
        defense = 6 + beast.level + rarity_mod * 2
        return cls(beast=beast, stats=CombatStats(base, attack, focus, defense), current_health=base)

    def apply_damage(self, amount: int) -> None:
        mitigated = max(0, amount - (self.stats.defense + self.guard_bonus) // 2)
        self.current_health = max(0, self.current_health - mitigated)
        self.guard_bonus = 0

    def heal(self, amount: int) -> None:
        self.current_health = min(self.stats.health, self.current_health + amount)


@dataclass
class CombatTurnLog:
    actor: str
    action: str
    result: str


class CombatEngine:
    def __init__(self, roster: List[BeastInstance], wild_templates: List[BeastTemplate]):
        self.roster = roster
        self.wild_templates = wild_templates
        self.turn_log: List[CombatTurnLog] = []

    def start_encounter(self, player_beast: BeastInstance) -> Tuple[CombatParticipant, CombatParticipant]:
        opponent_template = random.choice(self.wild_templates)
        opponent_instance = BeastInstance(template=opponent_template)
        opponent_instance.level = max(1, player_beast.level + random.randint(-1, 2))
        return CombatParticipant.from_beast(player_beast), CombatParticipant.from_beast(opponent_instance)

    def execute_turn(self, player: CombatParticipant, opponent: CombatParticipant, player_action: str) -> None:
        self.turn_log.clear()
        enemy_action = random.choice(COMBAT_ACTIONS)
        # Player resolves first
        self.turn_log.append(self._resolve_action(player, opponent, player_action))
        if opponent.current_health <= 0:
            return
        self.turn_log.append(self._resolve_action(opponent, player, enemy_action))
        if player.current_health <= 0:
            return

    def _resolve_action(self, actor: CombatParticipant, target: CombatParticipant, action: str) -> CombatTurnLog:
        if action == "Strike":
            damage = actor.stats.attack + random.randint(4, 10)
            target.apply_damage(damage)
            return CombatTurnLog(actor=actor.beast.template.name, action=action, result=f"deals {damage}!")
        if action == "Channel":
            damage = actor.stats.focus + random.randint(6, 12)
            target.apply_damage(damage)
            return CombatTurnLog(actor=actor.beast.template.name, action=action, result=f"casts for {damage}!")
        if action == "Guard":
            actor.guard_bonus = actor.stats.defense
            return CombatTurnLog(actor=actor.beast.template.name, action=action, result="raises guard")
        if action == "Heal":
            amount = actor.stats.focus // 2 + random.randint(5, 12)
            actor.heal(amount)
            return CombatTurnLog(actor=actor.beast.template.name, action=action, result=f"restores {amount}")
        return CombatTurnLog(actor=actor.beast.template.name, action=action, result="is confused")

    def conclude_battle(self, player: CombatParticipant, opponent: CombatParticipant) -> Dict[str, str]:
        result: Dict[str, str] = {}
        if player.current_health <= 0 and opponent.current_health <= 0:
            result["outcome"] = "Draw"
        elif opponent.current_health <= 0:
            result["outcome"] = "Victory"
            gain_experience(player.beast, 45)
        else:
            result["outcome"] = "Defeat"
        result["player_health"] = f"{player.current_health}/{player.stats.health}"
        result["opponent_health"] = f"{opponent.current_health}/{opponent.stats.health}"
        return result
