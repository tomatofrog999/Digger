
# Digger

A 2D digging game made with Pygame, where you explore the underground, dig through different layers of blocks, and collect resources along the way.

Start with limited energy and make every move count. Dig deeper to discover valuable resources, manage your energy, and earn money to purchase upgrades that help you progress further.

But be careful! The deeper you go, the more challenging things become. Dangerous blocks, limited resources, and increasing difficulty will make each run a little harder than the last.

## Features

### Player Movement
- **Basic Movement** - Move left and right using `A` and `D`, and jump using `Spacebar`.
- **Wall Slide** - Hold `A` or `D` while falling down beside the wall to slow down your falling speed.
- **Wall Jump** - Jump toward a wall and press `Spacebar` again to launch yourself in the opposite direction.

### Digging System
- **Directional Digging** - Use `J` or `K` to dig in the selected direction. Use `W`, `A`, `S`, or `D` to choose the digging direction.
- **Block Durability** - Block durability increases as you dig deeper to the new layer.
- **Rhythm Multiplier** - Dig in sync with the music notes to break blocks faster.
- **Rhythm Bar** - Displays the timing of the music notes to help you dig in rhythm.

### Block Types
- **Normal Blocks** - Basic blocks that when digging will drop block-unit.
- **Treasure Blocks** - Contain gem that can be exchanged for upgrades or refill energy or health.
- **Energy Blocks** - Restore energy when mined.
- **Trap Blocks** - Damage the player when breaking it.
- **Multi Blocks** - Blocks with different sizes, such as 2x2, adding variety to the underground layout.

### Player Status
- **Energy Bar** - Displays the player's remaining energy, which decreases when digging.
- **Health Bar** - Displays the player's health, which decreases when taking damage from traps.
- **Inventory System** - Collect and manage resources obtained from mining.

### Shops & Upgrades
- **Tavern** - Exchange collected treasures for energy.
- **Upgrade Shop** - Exchange treasures for equipment upgrades to improve your digging capabilities.

### Game Progression
- **Procedural Map Generation** - Generate underground maps with different block arrangements.
- **Increasing Difficulty** - The deeper you progress, the more challenging mining becomes.
- **Difficulty Scaling** - Block durability, energy consumption, and other challenges increase as you progress.


## Installation

### Install the base game dependencies

```bash
pip install -r requirements.txt
```

### Install the tool dependencies

```bash
pip install -r requirements_tool.txt
```

## How to run

```bash
python main.py
```
## Demo

```bash
 https://youtu.be/ZtiF1KLWSS8?si=-YSLSQpCmYkXjrgw
```
