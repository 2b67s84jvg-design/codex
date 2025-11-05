# Spellbound Sanctuary — Game Design Foundation

## Vision Statement
Spellbound Sanctuary is a cozy-yet-ambitious 2D life-sim RPG for iPhone where players adopt, raise, and battle an ever-growing menagerie of magical beasts. The experience blends nurturing, base building, and tactical turn-based combat into a daily ritual that rewards creativity, curiosity, and emotional connection with fantastical companions.

## Target Platform & Audience
- **Platform:** iOS (iPhone), portrait-first with responsive layouts for landscape battles.
- **Audience:** Fans of creature collectors, farm sims, and cozy strategy games (ages 12+).
- **Session Length:** 3–10 minute micro-sessions layered into longer progression loops.

## Core Pillars
1. **Nurture Meaningful Bonds** — Deep care mechanics (hunger, thirst, hygiene, happiness, energy) influence growth, mood, and battle performance.
2. **Evolving Sanctuary** — Build and customize a floating sanctuary island, leveraging beasts to gather magical resources and expand facilities.
3. **Strategic Fantastical Combat** — Accessible yet nuanced turn-based battles inspired by Pokémon, with elemental affinities, status effects, and duo skills.
4. **Surprise & Discovery** — Random egg hatching, branching evolutions, secret hybrid combinations, and island mysteries keep players experimenting.

## Game Loop Overview
1. **Daily Care**
   - Tend to beasts' needs (feed, water, groom, play) using interactive mini-games.
   - Monitor status meters: Hunger, Thirst, Cleanliness, Mood/Happiness, Energy, Bond, and Focus.
   - Respond to behavioral cues (animations, speech bubbles) to prevent debuffs or runaways.
2. **Sanctuary Management**
   - Construct and upgrade buildings: roosts, nurseries, training arenas, workshops, alchemy labs, elemental shrines, and expeditions dock.
   - Assign beasts to work posts (foraging, crafting, guarding). Productivity scales with mood and trait synergies.
   - Manage storage (up to 30 beast slots within the base; expand via dimensional vault upgrades).
3. **Exploration & Gathering**
   - Dispatch beasts on timed expeditions to biomes (Mystwood, Stormpeaks, Emberdeep, Abyssal Reef, Chromatic Desert, Starfall Ruins).
   - Harvest resources (lunar fruit, mana crystals, ether bark, stardust ore) and rare egg fragments.
4. **Battle & Events**
   - Engage in turn-based arena duels, guild trials, and seasonal tournaments.
   - Earn badges, rare reagents, hybrid catalysts, and reputation currency for cosmetics.
5. **Morphing & Breeding**
   - Pair compatible beasts in the Arcane Hatchery to hatch new eggs.
   - Specific pairs unlock secret hybrid forms with unique sprites, skills, and dual affinities.

## Creature Roster
Players can start with a curated selection or adopt a mystery egg (randomly determined upon hatching). Each beast has base stats, elemental affinity, favorite foods, personality traits, and work proficiencies. Below is the initial roster (25+ beasts):

| # | Beast | Element | Signature Trait | Favorite Job | Notable Hybrid Pairings |
|---|-------|---------|-----------------|--------------|-------------------------|
| 01 | **Lunarkit** | Moon | Shy Empath | Dreamkeeper | Lunarkit × Sunflit → **Eclipsea** |
| 02 | **Sunflit** | Solar | Radiant Aura | Pollinator | |
| 03 | **Brimrill** | Ember | Hardy Furnace | Smelter | Brimrill × Froscale → **Steamjaw** |
| 04 | **Froscale** | Frost | Calm Resilience | Fisher | |
| 05 | **Stormwisp** | Storm | Static Whirl | Weather Sage | Stormwisp × Terragore → **Tempesthorn** |
| 06 | **Terragore** | Earth | Gentle Giant | Quarry Worker | |
| 07 | **Sylphling** | Wind | Mischief Gale | Courier | Sylphling × Mirebrood → **Gossamer Toad** |
| 08 | **Mirebrood** | Swamp | Toxic Bloom | Alchemist | |
| 09 | **Aethermoth** | Arcane | Phase Drift | Archivist | Aethermoth × Glimmerfox → **Illusory Mothfox** |
| 10 | **Glimmerfox** | Light | Trickster Charm | Scout | |
| 11 | **Obsidrake** | Shadow | Veiled Fury | Defender | Obsidrake × Radiant Stag → **Nightprism Drake** |
| 12 | **Radiant Stag** | Aurora | Noble Guard | Beacon Keeper | |
| 13 | **Tidepurl** | Water | Bubble Buddy | Pearl Diver | Tidepurl × Emberfin → **Steam Siren** |
| 14 | **Emberfin** | Lava | Boiling Heart | Glassblower | |
| 15 | **Briarhoof** | Flora | Verdant Shield | Gardener | Briarhoof × Clockwarren → **Thicket Hare** |
| 16 | **Clockwarren** | Chrono | Timelapse | Tinkerer | |
| 17 | **Nebulyx** | Cosmic | Gravity Well | Star Harvester | Nebulyx × Quillvyrn → **Singularity Vyrn** |
| 18 | **Quillvyrn** | Crystal | Prism Spines | Miner | |
| 19 | **Voltursa** | Lightning | Thunder Roar | Sentinel | Voltursa × Dewsprite → **Stormsprite Bear** |
| 20 | **Dewsprite** | Mist | Rain Dancer | Healer | |
| 21 | **Ambercoil** | Metal | Magnetic Shell | Artisan | Ambercoil × Bloomspur → **Gilded Pollenbug** |
| 22 | **Bloomspur** | Fae | Pollen Pulse | Apothecarist | |
| 23 | **Wispurr** | Spirit | Echo Purr | Comforter | Wispurr × Huskfang → **Phantom Lynx** |
| 24 | **Huskfang** | Bone | Ossified Hide | Tracker | |
| 25 | **Galeserpent** | Air | Sky Dancer | Navigator | Galeserpent × Tidepurl → **Tempest Leviathan** |
| 26 | **Solblossom** | Solar/Flora | Solar Bloom | Orchardist | Solblossom × Frostvine → **Aurora Petal** |
| 27 | **Frostvine** | Frost/Flora | Crystal Bloom | Brewmaster | |

- Additional hybrids unlock by experimentation; not all combinations succeed, encouraging discovery.
- Mystery eggs have rarity tiers (Common, Uncommon, Rare, Legendary). Legendary eggs have a small chance to hatch hybrids immediately.

## Morphing & Breeding System
- **Arcane Compatibility:** Each beast has up to three compatible families; breeding outside them yields normal offspring with trait inheritance but no morph.
- **Hybrid Odds:** Successful morph chance depends on parent bond level, habitat alignment, and catalyst items. Base chance ~20%; catalysts can raise to 40%. Failed attempts still produce a pure offspring with inherited traits.
- **Inherited Traits:** Offspring inherit 2 random traits (stat modifiers, passive abilities) from parents; hybrid forms gain unique skill trees.
- **Egg Incubation:** Incubation mini-game affects hatch bonus (stat boost, exclusive moves, visual pattern variations).

## Care & Progression Systems
- **Meters & Effects:**
  - Hunger → Affects growth rate; starving lowers HP and mood.
  - Thirst → Lowers energy regeneration; dehydration causes negative status in combat.
  - Cleanliness → Impacts sickness risk; dirty beasts spread grime debuffs in facilities.
  - Mood/Happiness → Governs obedience, skill crit chance, and work efficiency.
  - Energy → Determines working hours and battle readiness.
  - Bond → Unlocks combo abilities, dialogue, and personal quests.
  - Focus → Enables special training sessions and critical success chance in crafting.
- **Care Activities:** Feeding (ingredient recipes), watering (elemental infusions), grooming (brushing, polishing scales), playtime (toys, mini-games), rest (beds, hammocks), training (stat gains but drains energy).
- **Status Conditions:** Sickness, Melancholy, Overgrowth, Arcane Burn, Stardaze; each requires specific remedies crafted in the Alchemy Lab.

## Sanctuary Base Features
- **Max Beast Capacity:** 30 slots by default; can expand via "Sky Vault" upgrades.
- **Building Categories:**
  - **Habitats:** Element-themed dens providing passive buffs and mood boosts.
  - **Utility:** Feeding hall, hydration spring, grooming spa, infirmary.
  - **Production:** Workshop, weaving loft, ore foundry, potionarium.
  - **Research:** Codex Library (unlock lore, skill upgrades), Divination Observatory (forecast weather events), Hybridarium (log breeding discoveries).
  - **Defense:** Barrier pylons, watch roosts; relevant for invasion events.
- **Resource Types:** Etherwood, Luminite Ore, Starwater, Gleamshards, Verdant Thread, Emberglass, Chronoweave.
- **Harvesting Loop:** Assign beasts to resource nodes—work shift mini-game determines yield quality. Traits give bonuses (e.g., Brimrill + Foundry = +20% Emberglass).
- **Construction Mechanics:**
  - Place modular tiles on a grid-based floating island; height levels unlocked via Sky Anchors.
  - Buildings require materials, construction time, and occasionally beast assistance (quick-time event to boost build speed).
  - Cosmetic placement items (lanterns, arcane gardens, murals) impact beast mood and player profile.
- **Event Hooks:** Lunar festivals, meteor showers, guild visitors, rival tamers, seasonal decor.

## Player Avatar
- **Models:** Two base humanoid sprites (masculine, feminine) with customizable skin tones, hairstyles, outfits, and magical auras.
- **Progression:** Unlock gear cosmetics via achievements, battles, and crafting.
- **Role:** Avatar performs manual tasks, interacts with beasts, and participates in mini-games.

## Combat System (Turn-Based)
- **Format:** 1v1 or 2v2 beast battles; player selects a primary beast and optional support.
- **Turn Flow:** Initiative determined by Speed stat; actions include Attack, Skill, Defend, Item, Swap.
- **Skill Types:** Physical, Elemental, Support, Ultimate (bond-gated). Moves consume Focus or Stamina.
- **Affinities:** Elemental rock-paper-scissors chart with dual-element hybrids creating unique resistances.
- **Status Effects:** Shocked, Frozen, Burnt, Rooted, Dazzled, Hexed, Time-Slip. Stackable buffs (Barrier, Haste) and debuffs (Vulnerability).
- **Synergy Actions:** High-bond pairs unlock "Duo Arts" (e.g., Lunarkit + Sunflit → Eclipse Nova).
- **Arena Progression:** Story arenas, ranked ladder, rogue-like "Dreamscapes" mode, asynchronous PvP ghosts.
- **Rewards:** Skill shards, rare materials, badges that unlock new buildings or cosmetics.

## Audio & Visual Direction
- **Art Style:** Hand-painted 2D sprites with parallax layered backgrounds, vibrant color palettes, and whimsical animation loops.
- **Beast Sprites:** Each beast has idle, happy, sad, hungry, thirsty, sleeping, working, and battle poses. Hybrids unlock variant palettes. Realistic magical-creature inspirations (gryphons, kitsune, leviathans, etc.).
- **UI:** Cozy spellbook aesthetic with tabs for Beasts, Base, Codex, and Arena. Haptic feedback for interactions.
- **Audio:** Ambient sanctuary soundtrack, adaptive battle music, creature vocalizations tied to mood.

## Monetization & Retention (High-Level)
- **Premium Purchase:** One-time premium game with optional cosmetic expansions.
- **Daily Rituals:** Login gifts, rotating quests, special events, collaborative community goals.
- **Cloud Saves & Offline Play:** Autosave with iCloud sync for continuity.

## Technical Foundation Notes
- **Engine:** Unity or Godot (evaluate for 2D pipeline and mobile performance).
- **Data:** Scriptable objects or JSON-based config for beasts, buildings, and items (see `data/beasts.json` for initial structure).
- **Systems Roadmap:** Prioritize care loop and base building in prototype; integrate combat after establishing creature data and animation pipelines.

## Next Steps
1. Flesh out beast stat blocks, skill lists, and animation requirements.
2. Prototype care UI and base grid placement in engine of choice.
3. Implement egg hatching flow with randomization, incubation mini-game, and hybrid logic.
4. Develop initial combat prototype with 1v1 battles and three core elements (expand later).
5. Build content pipeline for sprites, sounds, and localization.
