# Sunheart Reliquary - Prototype

This repository contains a ready-to-play 2D survival RPG prototype set in the Peruvian Amazon. You step into the role of archaeologist **Dr. Elena Marín**, stranded in the jungle after a landslide scatters her expedition. Survive long enough to follow the trail to the Sunheart Reliquary by gathering resources, mastering the environment, and building a safe camp.

## Highlighted Features

- **Scrollable jungle sandbox** with a 64×64 tile world, varied biomes (forest, bog, ruins, waterways), weather shifts, and a full day/night cycle.
- **Vitals-driven survival** covering health, hunger, thirst, stamina, and sanity with contextual modifiers for rain, mist, and nearby campfires.
- **Resource gathering and hunting** for wood, stone, herbs, resin, fibers, fresh water, and wildlife that yields raw meat.
- **Crafting and base building** including early tools (stone knife, hand axe, rope, torch), medical supplies, cooked meals, and placeable structures (campfire, lean-to, water collector, garden plot).
- **Quest log and guidance** that rewards progress with materials and keeps the player focused on story-driven objectives.
- **Full HUD suite** featuring vitals bars, weather readout, quest tracker, inventory, crafting lists, build planner, rotating tips, and activity log.

## Controls

| Input | Action |
| --- | --- |
| WASD | Move |
| Left Shift | Sprint (consumes stamina) |
| E | Gather nearby resources, structure yields, or fresh water |
| Space | Hunt wildlife / confirm build placement |
| F / G / H / J / K | Consume food / water / bandage / herb / cooked meat |
| 1-6 | Craft available recipes |
| Tab | Toggle inventory panel |
| C | Toggle crafting panel |
| B | Toggle build mode (use ←/→ or A/D to select, Enter/Space to place) |
| Esc | Pause |

## Getting Started

1. (Optional) Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Launch the prototype:

   ```bash
   python main.py
   ```

The game opens a Pygame window with keyboard-only controls. Gather materials, craft better gear, and construct shelters to keep Elena alive. Watch the HUD message log for contextual feedback and objective progress.

## Next Steps & Extension Ideas

- Expand biome diversity (cenotes, floodplains, canopy walkways) and add traversal tools like ziplines or climbing gear.
- Layer in narrative encounters with Mayan spirit guardians and rival treasure hunters that react to player choices.
- Grow the crafting tree into multi-stage technology, introducing metallurgy, advanced medicine, and permanent structures.
- Implement audio, particle effects, and bespoke art to bring the Amazon to life.

Contributions and experimentation are encouraged—fork the project, tweak settings, and prototype new mechanics.
