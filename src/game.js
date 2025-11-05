const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const progressBars = {
  health: document.getElementById("health-bar"),
  hunger: document.getElementById("hunger-bar"),
  thirst: document.getElementById("thirst-bar"),
  stamina: document.getElementById("stamina-bar"),
  sanity: document.getElementById("sanity-bar"),
};
const timeWeatherEl = document.getElementById("time-weather");
const questLogEl = document.getElementById("quest-log");
const inventoryEl = document.getElementById("inventory");
const messageLogEl = document.getElementById("message-log");
const gatherBtn = document.getElementById("gather-btn");
const restBtn = document.getElementById("rest-btn");
const craftBtn = document.getElementById("craft-btn");
const consumeBtn = document.getElementById("consume-btn");
const dpad = document.querySelectorAll("#controls button[data-dir]");

const TILE_SIZE = 24;
const WORLD_WIDTH = 80;
const WORLD_HEIGHT = 60;

const viewport = {
  width: canvas.width,
  height: canvas.height,
  scale: 1,
};

let viewTilesX = Math.max(8, Math.floor(canvas.width / TILE_SIZE));
let viewTilesY = Math.max(8, Math.floor(canvas.height / TILE_SIZE));
const lastViewport = { width: 0, height: 0, scale: 0 };

const DIRECTIONS = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

const TILE_TYPES = {
  forest: { color: "#0f3f2a", passable: true },
  clearing: { color: "#1a6339", passable: true },
  water: { color: "#134f63", passable: false },
  ruins: { color: "#52443f", passable: true },
  bog: { color: "#2a402a", passable: true, staminaMultiplier: 0.6 },
};

const RESOURCE_TYPES = {
  wood: { color: "#785734", gatheringTime: 1.4 },
  stone: { color: "#909090", gatheringTime: 1.6 },
  herb: { color: "#6bd69f", gatheringTime: 1.2 },
  water: { color: "#5bc2e7", gatheringTime: 1.0 },
  food: { color: "#e0a75d", gatheringTime: 1.8 },
};

const STRUCTURE_TYPES = {
  campfire: {
    cost: { wood: 3, stone: 1 },
    aura: 3,
    effects: { stamina: 15, sanity: 10 },
    color: "#d06030",
  },
  leanTo: {
    cost: { wood: 5, herb: 2 },
    aura: 3,
    effects: { stamina: 25, sanity: 20 },
    color: "#b6a16f",
  },
  waterCollector: {
    cost: { wood: 2, stone: 2 },
    aura: 2,
    effects: { thirst: 30 },
    color: "#4a8fbf",
  },
};

const QUESTS = [
  {
    id: "survive-night",
    title: "Secure Shelter",
    description: "Gather wood and craft a campfire before nightfall.",
    condition: state =>
      state.inventory.wood >= 3 &&
      state.inventory.stone >= 1 &&
      state.structures.some(s => s.type === "campfire"),
  },
  {
    id: "first-harvest",
    title: "Sustain Yourself",
    description: "Collect food, boil water, and keep hunger and thirst above 50.",
    condition: state =>
      state.inventory.food >= 2 &&
      state.inventory.water >= 2 &&
      state.vitals.hunger > 50 &&
      state.vitals.thirst > 50,
  },
  {
    id: "decode-glyph",
    title: "Decode a Glyph",
    description: "Explore the jungle ruins to find a glyph stone.",
    condition: state => state.discoveries.includes("glyph"),
  },
];

const inputState = { up: false, down: false, left: false, right: false };
const activeTouches = new Map();
const messageLog = [];

const state = {
  world: generateWorld(WORLD_WIDTH, WORLD_HEIGHT),
  resources: generateResources(140),
  glyphs: generateGlyphs(6),
  structures: [],
  discoveries: [],
  timeOfDay: 0,
  day: 1,
  weather: "Clear",
  weatherTimer: 0,
  vitals: {
    health: 100,
    hunger: 100,
    thirst: 100,
    stamina: 100,
    sanity: 100,
  },
  inventory: {
    wood: 0,
    stone: 0,
    herb: 0,
    water: 1,
    food: 1,
    rope: 0,
    flint: 0,
  },
  player: {
    x: Math.floor(WORLD_WIDTH / 2),
    y: Math.floor(WORLD_HEIGHT / 2),
    speed: 6,
    gatherCooldown: 0,
  },
};

function syncCanvasSize(force = false) {
  const displayWidth = Math.floor(
    canvas.clientWidth || canvas.offsetWidth || canvas.width / Math.max(viewport.scale, 1) || canvas.width
  );
  const displayHeight = Math.floor(
    canvas.clientHeight || canvas.offsetHeight || canvas.height / Math.max(viewport.scale, 1) || canvas.height
  );
  if (!displayWidth || !displayHeight) {
    return;
  }

  const scale = Math.min(window.devicePixelRatio || 1, 2);
  if (
    !force &&
    displayWidth === lastViewport.width &&
    displayHeight === lastViewport.height &&
    scale === lastViewport.scale
  ) {
    return;
  }

  viewport.width = displayWidth;
  viewport.height = displayHeight;
  viewport.scale = scale;

  const requiredWidth = Math.floor(displayWidth * scale);
  const requiredHeight = Math.floor(displayHeight * scale);
  if (canvas.width !== requiredWidth || canvas.height !== requiredHeight) {
    canvas.width = requiredWidth;
    canvas.height = requiredHeight;
  }

  ctx.setTransform(scale, 0, 0, scale, 0, 0);
  ctx.imageSmoothingEnabled = false;

  viewTilesX = Math.max(8, Math.floor(displayWidth / TILE_SIZE));
  viewTilesY = Math.max(8, Math.floor(displayHeight / TILE_SIZE));

  lastViewport.width = displayWidth;
  lastViewport.height = displayHeight;
  lastViewport.scale = scale;
}

function generateWorld(width, height) {
  const tiles = Array.from({ length: height }, (_, y) =>
    Array.from({ length: width }, (_, x) => {
      const edge = x < 5 || y < 5 || x > width - 6 || y > height - 6;
      const noise = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453;
      const random = noise - Math.floor(noise);
      if (edge && random < 0.45) return "water";
      if (random > 0.82) return "water";
      if (random > 0.7) return "bog";
      if (random > 0.5) return "ruins";
      if (random > 0.25) return "forest";
      return "clearing";
    })
  );

  ensureWalkableCenter(tiles);
  return tiles;
}

function ensureWalkableCenter(tiles) {
  const centerX = Math.floor(tiles[0].length / 2);
  const centerY = Math.floor(tiles.length / 2);
  for (let y = -2; y <= 2; y++) {
    for (let x = -2; x <= 2; x++) {
      const tx = centerX + x;
      const ty = centerY + y;
      if (tiles[ty] && tiles[ty][tx]) {
        tiles[ty][tx] = "clearing";
      }
    }
  }
}

function generateResources(count) {
  const resources = [];
  for (let i = 0; i < count; i++) {
    const type = randomWeighted([
      { value: "wood", weight: 3 },
      { value: "stone", weight: 2 },
      { value: "herb", weight: 2 },
      { value: "water", weight: 1 },
      { value: "food", weight: 1.4 },
    ]);
    const position = randomPassableTile();
    resources.push({
      id: `resource-${i}`,
      type,
      amount: 2 + Math.floor(Math.random() * 3),
      ...position,
    });
  }
  return resources;
}

function generateGlyphs(count) {
  const glyphs = [];
  for (let i = 0; i < count; i++) {
    const position = randomPassableTile();
    glyphs.push({ id: `glyph-${i}`, discovered: false, ...position });
  }
  return glyphs;
}

function randomPassableTile() {
  for (let attempts = 0; attempts < 500; attempts++) {
    const x = Math.floor(Math.random() * WORLD_WIDTH);
    const y = Math.floor(Math.random() * WORLD_HEIGHT);
    const tile = state?.world?.[y]?.[x] ?? "clearing";
    if (TILE_TYPES[tile].passable) {
      return { x, y };
    }
  }
  return { x: Math.floor(WORLD_WIDTH / 2), y: Math.floor(WORLD_HEIGHT / 2) };
}

function randomWeighted(values) {
  const total = values.reduce((sum, v) => sum + v.weight, 0);
  let threshold = Math.random() * total;
  for (const entry of values) {
    if ((threshold -= entry.weight) <= 0) {
      return entry.value;
    }
  }
  return values[0].value;
}

function logMessage(text, options = {}) {
  messageLog.unshift({
    text,
    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    type: options.type ?? "info",
  });
  if (messageLog.length > 8) {
    messageLog.pop();
  }
  renderMessageLog();
}

function renderMessageLog() {
  messageLogEl.innerHTML = messageLog
    .map(msg => `<p><strong>${msg.time}</strong> — ${msg.text}</p>`)
    .join("");
}

function update(timeDelta) {
  tickWeather(timeDelta);
  tickTime(timeDelta);
  tickVitals(timeDelta);
  handleMovement(timeDelta);
  updateGlyphs();
  updateHUD();
  updateQuestLog();
}

function tickTime(delta) {
  state.timeOfDay += delta * 0.01;
  if (state.timeOfDay >= 1) {
    state.timeOfDay -= 1;
    state.day += 1;
    logMessage(`Day ${state.day} dawns over the canopy.`);
  }
}

function tickWeather(delta) {
  state.weatherTimer -= delta;
  if (state.weatherTimer <= 0) {
    const options = ["Clear", "Misty", "Rain", "Storm"];
    const last = state.weather;
    state.weather = options[Math.floor(Math.random() * options.length)];
    state.weatherTimer = 45 + Math.random() * 60;
    if (state.weather !== last) {
      logMessage(`The weather shifts to ${state.weather.toLowerCase()}.`);
    }
  }
}

function tickVitals(delta) {
  const weather = state.weather;
  const hungerDrain = 1 + (weather === "Storm" ? 0.5 : 0);
  const thirstDrain = 1 + (weather === "Rain" ? -0.2 : weather === "Heat" ? 0.8 : 0);

  state.vitals.hunger = Math.max(0, state.vitals.hunger - hungerDrain * delta * 1.2);
  state.vitals.thirst = Math.max(0, state.vitals.thirst - (1 + thirstDrain) * delta * 1.4);
  state.vitals.stamina = Math.max(0, state.vitals.stamina - delta * 2);

  const hungerPenalty = state.vitals.hunger < 20 ? 0.8 : 0;
  const thirstPenalty = state.vitals.thirst < 20 ? 0.8 : 0;
  const sanityDecay = (state.vitals.hunger < 30 || state.vitals.thirst < 30) ? 0.8 : 0.3;
  state.vitals.sanity = Math.max(0, state.vitals.sanity - sanityDecay * delta);

  if (state.vitals.hunger === 0 || state.vitals.thirst === 0) {
    state.vitals.health = Math.max(0, state.vitals.health - delta * 4);
  } else {
    state.vitals.health = Math.min(100, state.vitals.health + delta * 2);
  }

  if (state.vitals.health <= 0) {
    logMessage("You collapse. The jungle reclaims you.", { type: "danger" });
    resetRun();
  }
}

function resetRun() {
  state.vitals = { health: 100, hunger: 80, thirst: 80, stamina: 80, sanity: 90 };
  state.inventory = { wood: 0, stone: 0, herb: 0, water: 1, food: 1, rope: 0, flint: 0 };
  state.structures = [];
  state.discoveries = [];
  state.player.x = Math.floor(WORLD_WIDTH / 2);
  state.player.y = Math.floor(WORLD_HEIGHT / 2);
  state.resources = generateResources(120);
  logMessage("You awaken back at the crash site.");
}

function handleMovement(delta) {
  let dx = 0;
  let dy = 0;
  if (inputState.up) dy -= 1;
  if (inputState.down) dy += 1;
  if (inputState.left) dx -= 1;
  if (inputState.right) dx += 1;

  if (dx === 0 && dy === 0) {
    state.vitals.stamina = Math.min(100, state.vitals.stamina + delta * 10);
    return;
  }

  const tile = TILE_TYPES[state.world[state.player.y][state.player.x]];
  const speedMultiplier = tile.staminaMultiplier ?? 1;
  const speed = state.player.speed * speedMultiplier;
  const length = Math.hypot(dx, dy) || 1;
  const stepX = (dx / length) * speed * delta;
  const stepY = (dy / length) * speed * delta;

  attemptMove(stepX, stepY);
}

function attemptMove(stepX, stepY) {
  const nextX = state.player.x + stepX;
  const nextY = state.player.y + stepY;
  const tileX = Math.round(nextX);
  const tileY = Math.round(nextY);
  if (!withinBounds(tileX, tileY)) return;
  const tile = TILE_TYPES[state.world[tileY][tileX]];
  if (!tile.passable) return;
  state.player.x = nextX;
  state.player.y = nextY;
}

function withinBounds(x, y) {
  return x >= 0 && y >= 0 && x < WORLD_WIDTH && y < WORLD_HEIGHT;
}

function updateGlyphs() {
  for (const glyph of state.glyphs) {
    if (!glyph.discovered) {
      const distance = Math.hypot(glyph.x - state.player.x, glyph.y - state.player.y);
      if (distance < 1.2) {
        glyph.discovered = true;
        if (!state.discoveries.includes("glyph")) {
          state.discoveries.push("glyph");
        }
        logMessage("You record the glyph's meaning in your journal.");
      }
    }
  }
}

function updateHUD() {
  for (const vital of Object.keys(progressBars)) {
    progressBars[vital].value = state.vitals[vital];
  }

  const hours = Math.floor(state.timeOfDay * 24);
  const minutes = Math.floor((state.timeOfDay * 24 - hours) * 60)
    .toString()
    .padStart(2, "0");
  const cycle = state.timeOfDay < 0.25 || state.timeOfDay > 0.75 ? "Night" : "Day";
  timeWeatherEl.textContent = `Day ${state.day} • ${hours}:${minutes} • ${cycle} • ${state.weather}`;

  const inventoryText = Object.entries(state.inventory)
    .map(([key, value]) => `${formatLabel(key)}: ${value}`)
    .join(" | ");
  inventoryEl.textContent = inventoryText;
}

function updateQuestLog() {
  const items = QUESTS.map(quest => {
    const complete = quest.condition(state);
    return `<div class="quest ${complete ? "complete" : ""}">
      <strong>${quest.title}</strong>
      <p>${quest.description}</p>
    </div>`;
  }).join("");
  questLogEl.innerHTML = items;
}

function formatLabel(label) {
  return label
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, c => c.toUpperCase())
    .replace(/_/g, " ");
}

function draw() {
  ctx.clearRect(0, 0, viewport.width, viewport.height);
  const offsetX = state.player.x - viewTilesX / 2;
  const offsetY = state.player.y - viewTilesY / 2;

  for (let y = 0; y < viewTilesY + 2; y++) {
    for (let x = 0; x < viewTilesX + 2; x++) {
      const worldX = Math.floor(offsetX + x);
      const worldY = Math.floor(offsetY + y);
      if (!withinBounds(worldX, worldY)) continue;
      const tile = TILE_TYPES[state.world[worldY][worldX]];
      ctx.fillStyle = tile.color;
      ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
    }
  }

  drawGlyphs(offsetX, offsetY);
  drawResources(offsetX, offsetY);
  drawStructures(offsetX, offsetY);
  drawPlayer();
  drawLighting();
}

function drawPlayer() {
  ctx.save();
  ctx.fillStyle = "#f5d97e";
  ctx.beginPath();
  ctx.arc(viewport.width / 2, viewport.height / 2, TILE_SIZE / 2.6, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawResources(offsetX, offsetY) {
  for (const resource of state.resources) {
    if (resource.amount <= 0) continue;
    const screenX = (resource.x - offsetX) * TILE_SIZE;
    const screenY = (resource.y - offsetY) * TILE_SIZE;
    ctx.fillStyle = RESOURCE_TYPES[resource.type].color;
    ctx.fillRect(screenX + 6, screenY + 6, TILE_SIZE - 12, TILE_SIZE - 12);
  }
}

function drawGlyphs(offsetX, offsetY) {
  ctx.save();
  ctx.fillStyle = "#fbeaae";
  for (const glyph of state.glyphs) {
    const screenX = (glyph.x - offsetX) * TILE_SIZE;
    const screenY = (glyph.y - offsetY) * TILE_SIZE;
    ctx.globalAlpha = glyph.discovered ? 0.8 : 0.5;
    ctx.fillRect(screenX + 8, screenY + 8, TILE_SIZE - 16, TILE_SIZE - 16);
  }
  ctx.restore();
}

function drawStructures(offsetX, offsetY) {
  for (const structure of state.structures) {
    const screenX = (structure.x - offsetX) * TILE_SIZE;
    const screenY = (structure.y - offsetY) * TILE_SIZE;
    ctx.fillStyle = STRUCTURE_TYPES[structure.type].color;
    ctx.fillRect(screenX + 4, screenY + 4, TILE_SIZE - 8, TILE_SIZE - 8);
  }
}

function drawLighting() {
  const gradient = ctx.createRadialGradient(
    viewport.width / 2,
    viewport.height / 2,
    TILE_SIZE,
    viewport.width / 2,
    viewport.height / 2,
    viewport.width / 1.2
  );
  const darkness = state.timeOfDay < 0.25 || state.timeOfDay > 0.75 ? 0.7 : 0.2;
  gradient.addColorStop(0, "rgba(0,0,0,0)");
  gradient.addColorStop(1, `rgba(0,0,0,${darkness})`);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, viewport.width, viewport.height);
}

function gatherResource() {
  if (state.player.gatherCooldown > 0) return;
  const target = closestResource(1.2);
  if (!target) {
    logMessage("Nothing useful nearby.");
    return;
  }
  target.amount -= 1;
  state.player.gatherCooldown = RESOURCE_TYPES[target.type].gatheringTime;
  state.inventory[target.type] = (state.inventory[target.type] ?? 0) + 1;
  state.vitals.stamina = Math.max(0, state.vitals.stamina - 8);
  state.vitals.hunger = Math.max(0, state.vitals.hunger - 2);
  logMessage(`Collected ${target.type}.`);
}

function closestResource(range) {
  let nearest = null;
  let shortest = range + 1;
  for (const resource of state.resources) {
    if (resource.amount <= 0) continue;
    const distance = Math.hypot(resource.x - state.player.x, resource.y - state.player.y);
    if (distance < range && distance < shortest) {
      nearest = resource;
      shortest = distance;
    }
  }
  return nearest;
}

function rest() {
  const auraEffect = state.structures.reduce(
    (effect, structure) => {
      const def = STRUCTURE_TYPES[structure.type];
      const dist = Math.hypot(structure.x - state.player.x, structure.y - state.player.y);
      if (dist <= def.aura) {
        for (const [key, value] of Object.entries(def.effects)) {
          effect[key] = (effect[key] ?? 0) + value;
        }
      }
      return effect;
    },
    {}
  );

  if (Object.keys(auraEffect).length === 0) {
    logMessage("Resting in the wild offers little comfort.");
  }

  for (const [key, value] of Object.entries(auraEffect)) {
    if (key in state.vitals) {
      state.vitals[key] = Math.min(100, state.vitals[key] + value);
    }
  }
  state.vitals.stamina = Math.min(100, state.vitals.stamina + 20);
  state.vitals.sanity = Math.min(100, state.vitals.sanity + 10);
  state.vitals.health = Math.min(100, state.vitals.health + 8);
  logMessage("You take a moment to steady yourself.");
}

function craft() {
  const craftable = Object.entries(STRUCTURE_TYPES).find(([type, def]) =>
    canAfford(def.cost)
  );
  if (!craftable) {
    logMessage("You need more materials to craft a structure.");
    return;
  }
  const [type, def] = craftable;
  for (const [resource, amount] of Object.entries(def.cost)) {
    state.inventory[resource] -= amount;
  }
  const position = {
    x: Math.round(state.player.x + (Math.random() > 0.5 ? 1 : -1) * 2),
    y: Math.round(state.player.y + (Math.random() > 0.5 ? 1 : -1) * 2),
  };
  if (!withinBounds(position.x, position.y)) {
    position.x = Math.round(state.player.x);
    position.y = Math.round(state.player.y);
  }
  state.structures.push({ type, ...position });
  logMessage(`You assemble a ${formatLabel(type)}.`);
}

function canAfford(cost) {
  return Object.entries(cost).every(([resource, amount]) =>
    (state.inventory[resource] ?? 0) >= amount
  );
}

function consume() {
  if (state.inventory.food <= 0 && state.inventory.water <= 0) {
    logMessage("You have nothing left to consume.");
    return;
  }
  if (state.inventory.food > 0) {
    state.inventory.food -= 1;
    state.vitals.hunger = Math.min(100, state.vitals.hunger + 35);
    state.vitals.health = Math.min(100, state.vitals.health + 5);
    logMessage("You eat a cooked meal.");
  }
  if (state.inventory.water > 0) {
    state.inventory.water -= 1;
    state.vitals.thirst = Math.min(100, state.vitals.thirst + 40);
    logMessage("You drink filtered water.");
  }
}

function updateGatherCooldown(delta) {
  if (state.player.gatherCooldown > 0) {
    state.player.gatherCooldown = Math.max(0, state.player.gatherCooldown - delta);
  }
}

function gameLoop(timestamp) {
  syncCanvasSize();
  if (!gameLoop.last) gameLoop.last = timestamp;
  const delta = Math.min((timestamp - gameLoop.last) / 1000, 0.25);
  gameLoop.last = timestamp;
  updateGatherCooldown(delta);
  update(delta);
  draw();
  requestAnimationFrame(gameLoop);
}

function bindInputs() {
  window.addEventListener("keydown", event => {
    if (event.repeat) return;
    switch (event.key) {
      case "ArrowUp":
      case "w":
      case "W":
        inputState.up = true;
        break;
      case "ArrowDown":
      case "s":
      case "S":
        inputState.down = true;
        break;
      case "ArrowLeft":
      case "a":
      case "A":
        inputState.left = true;
        break;
      case "ArrowRight":
      case "d":
      case "D":
        inputState.right = true;
        break;
      case " ":
        gatherResource();
        break;
      case "e":
      case "E":
        gatherResource();
        break;
      case "r":
      case "R":
        rest();
        break;
      case "c":
      case "C":
        craft();
        break;
    }
  });

  window.addEventListener("keyup", event => {
    switch (event.key) {
      case "ArrowUp":
      case "w":
      case "W":
        inputState.up = false;
        break;
      case "ArrowDown":
      case "s":
      case "S":
        inputState.down = false;
        break;
      case "ArrowLeft":
      case "a":
      case "A":
        inputState.left = false;
        break;
      case "ArrowRight":
      case "d":
      case "D":
        inputState.right = false;
        break;
    }
  });

  for (const button of dpad) {
    const direction = button.dataset.dir;
    const handler = event => {
      event.preventDefault();
      inputState[direction] = true;
      activeTouches.set(event.pointerId ?? direction, direction);
    };
    const release = event => {
      const id = event.pointerId ?? direction;
      activeTouches.delete(id);
      inputState[direction] = false;
    };

    button.addEventListener("touchstart", handler, { passive: false });
    button.addEventListener("touchend", release);
    button.addEventListener("touchcancel", release);
    button.addEventListener("mousedown", handler);
    button.addEventListener("mouseup", release);
    button.addEventListener("mouseleave", release);
  }

  gatherBtn.addEventListener("click", gatherResource);
  restBtn.addEventListener("click", rest);
  craftBtn.addEventListener("click", craft);
  consumeBtn.addEventListener("click", consume);
}

function bootstrap() {
  syncCanvasSize(true);
  bindInputs();
  updateHUD();
  updateQuestLog();
  logMessage("You regain consciousness amidst the wreckage.");
  window.addEventListener("resize", () => syncCanvasSize(true));
  window.addEventListener("orientationchange", () => {
    setTimeout(() => syncCanvasSize(true), 200);
  });
  if (window.visualViewport) {
    window.visualViewport.addEventListener("resize", () => syncCanvasSize(true));
  }
  requestAnimationFrame(gameLoop);
}

bootstrap();
