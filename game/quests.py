"""Quest tracking for the survival RPG."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List

from . import settings

Condition = Callable[["QuestContext"], bool]
Reward = Dict[str, int]


@dataclass
class QuestContext:
    player: "Player"
    world: "World"


@dataclass
class Quest:
    identifier: str
    title: str
    description: str
    condition: Condition
    reward: Reward | None = None
    completed: bool = False

    def check(self, ctx: QuestContext) -> bool:
        if self.completed:
            return True
        if self.condition(ctx):
            self.completed = True
            if self.reward:
                for item, amount in self.reward.items():
                    ctx.player.add_item(item, amount)
            return True
        return False


@dataclass
class QuestLog:
    quests: List[Quest] = field(default_factory=list)
    current_index: int = 0

    def active(self) -> Quest | None:
        while self.current_index < len(self.quests) and self.quests[self.current_index].completed:
            self.current_index += 1
        if self.current_index < len(self.quests):
            return self.quests[self.current_index]
        return None

    def update(self, ctx: QuestContext) -> list[str]:
        messages: list[str] = []
        quest = self.active()
        if quest and quest.check(ctx):
            messages.append(f"Quest complete: {quest.title}")
            if quest.reward:
                reward_items = ", ".join(f"{item} x{amount}" for item, amount in quest.reward.items())
                messages.append(f"Rewards received: {reward_items}")
        return messages

    def objectives(self) -> Iterable[str]:
        quest = self.active()
        if quest:
            yield quest.title
            yield quest.description
        else:
            yield "All objectives complete"


from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - avoid cycle at runtime
    from .player import Player
    from .world import World


def default_quests() -> QuestLog:
    quests = [
        Quest(
            identifier="wood_gathering",
            title="Stabilize the Camp",
            description="Collect 5 wood and 3 stone to rebuild your supplies.",
            condition=lambda ctx: ctx.player.inventory.get("wood", 0) >= 5
            and ctx.player.inventory.get("stone", 0) >= 3,
            reward=settings.QUEST_REWARDS.get("wood_gathering"),
        ),
        Quest(
            identifier="first_fire",
            title="Light the Night",
            description="Construct a campfire to keep spirits at bay.",
            condition=lambda ctx: ctx.world.has_structure("campfire"),
            reward=settings.QUEST_REWARDS.get("first_fire"),
        ),
        Quest(
            identifier="secure_water",
            title="Secure Safe Water",
            description="Place a water collector to harvest rain.",
            condition=lambda ctx: ctx.world.has_structure("water_collector"),
            reward=settings.QUEST_REWARDS.get("secure_water"),
        ),
    ]
    return QuestLog(quests=quests)
