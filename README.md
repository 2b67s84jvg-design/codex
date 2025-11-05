# Spellbound Sanctuary Playable Prototype

This repository now ships a playable Python prototype for **Spellbound Sanctuary**, a 2D magical beast caretaker RPG concept targeting iPhone. It bundles the original concept documentation, a rich beast roster, and a desktop-friendly game loop that demonstrates core care, base-building, breeding, and combat systems.

## Getting Started

1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Launch the prototype:

   ```bash
   python main.py
   ```

The prototype runs on desktop via Pygame but is organized so its systems can be ported to mobile frameworks.

## Gameplay Overview

* **Caretaker Selection** — Choose between two distinct avatar models (Arcanist Rowan or Seeress Lyra) before entering the sanctuary.
* **Beast Adoption** — Adopt one of 27 bespoke magical beasts from `data/beasts.json`, or gamble on a mystery egg that hatches into a surprise companion.
* **Care Systems** — Monitor hunger, thirst, mood, and energy meters; feed, hydrate, play, and rest to keep companions thriving.
* **Tasking & Harvesting** — Assign beasts to forage, gather, or scout missions to earn stardust, essence, crystal, and herbs while gaining experience.
* **Base Building** — Spend resources on unique structures that unlock perks and increase the sanctuary’s capacity of up to 30 beasts.
* **Breeding & Hybrids** — Pair compatible beasts to incubate eggs and roll for hybrid outcomes using the roster’s combo data.
* **Turn-Based Combat** — Challenge wild foes in a Pokémon-inspired encounter system with strike, channel, guard, and heal actions.

## Repository Contents

- `main.py` — game entry point and state orchestration.
- `game/` — core gameplay modules (UI widgets, beast management, base simulation, combat engine, constants).
- `data/beasts.json` — roster of 27 magical beasts, their affinities, and hybrid pairings.
- `docs/magical_pet_game_design.md` — original high-level design document for reference.

Feel free to iterate on art, audio, or engine integration while reusing the mechanics scaffolded here.
