# Sunheart Reliquary (Web Edition)

A touch-first 2D survival RPG that runs directly in the browser, designed to be playable on iPhone, iPad, and desktop browsers without installing native dependencies. Explore the Amazon rainforest as archaeologist **Dr. Elena Marín**, balance vital needs, collect resources, build makeshift shelters, and decipher Mayan glyphs in search of the Sunheart Reliquary.

## Play the Prototype

1. Start a static web server in the repository root. Any host will work; for an option that does not require installing additional packages, use Python:

   ```bash
   python -m http.server 8000
   ```

   Keep the terminal open so the server continues running.

2. Visit the served address (e.g., `http://localhost:8000`) from your desktop browser or Safari on iPhone/iPad. Use the “Share” menu → **Add to Home Screen** on iOS for a full-screen experience with the on-screen controls.

## Controls

### Desktop
- **WASD / Arrow keys** – Move
- **Space / E** – Gather nearest resource
- **R** – Rest (recovers stamina, sanity, and health)
- **C** – Craft (builds the best available structure)

### Touch (Mobile)
- On-screen **directional pad** – Move
- **Gather**, **Rest**, **Craft**, **Consume** buttons – Perform interactions

## Core Features
- **Procedural jungle map** with water hazards, bogs that slow movement, and ruins hiding glyph stones.
- **Resource harvesting** for wood, stone, herbs, food, and water with stamina, hunger, and thirst trade-offs.
- **Structure crafting** (campfire, lean-to, and water collector) that create restorative auras and help you survive multi-day runs.
- **Survival vitals** (health, hunger, thirst, stamina, sanity) that drain based on weather, time of day, and player actions.
- **Dynamic weather and day/night cycle** that influence resource depletion and visibility.
- **Quest log** that guides early objectives such as crafting your first campfire and deciphering jungle glyphs.
- **Accessible HUD** with large touch targets, clear progress bars, and screen reader-friendly updates.

## Extending the Game
- Add additional biomes (cenotes, canopy walkways) and traversal tools such as ropes and ziplines.
- Introduce wildlife encounters with stealth and combat mechanics.
- Expand crafting tiers with metallurgy, medicine, and base fortifications.
- Persist world state between sessions using local storage or a backend service.

## Development Checks

Run a quick syntax verification before committing changes:

```bash
node --check src/game.js
```

This repository avoids network-dependent tooling so it can be worked on offline or in restricted environments.

Contributions are welcome—fork the project, experiment with new mechanics, and share your discoveries.
