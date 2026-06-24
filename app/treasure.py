import random

GEMS = {
    "low": [
        "Azurite (10 gp)", "Banded Agate (10 gp)", "Blue Quartz (10 gp)",
        "Eye Agate (10 gp)", "Hematite (10 gp)", "Lapis Lazuli (10 gp)",
        "Malachite (10 gp)", "Moss Agate (10 gp)", "Obsidian (10 gp)",
        "Tiger Eye (10 gp)", "Turquoise (10 gp)",
    ],
    "mid": [
        "Bloodstone (50 gp)", "Carnelian (50 gp)", "Citrine (50 gp)",
        "Jasper (50 gp)", "Moonstone (50 gp)", "Onyx (50 gp)",
        "Sardonyx (50 gp)", "Zircon (50 gp)", "Amber (100 gp)",
        "Amethyst (100 gp)", "Coral (100 gp)", "Garnet (100 gp)",
        "Jade (100 gp)", "Pearl (100 gp)", "Tourmaline (100 gp)",
    ],
    "high": [
        "Alexandrite (500 gp)", "Aquamarine (500 gp)", "Black Pearl (500 gp)",
        "Peridot (500 gp)", "Topaz (500 gp)", "Black Opal (1,000 gp)",
        "Blue Sapphire (1,000 gp)", "Emerald (1,000 gp)", "Fire Opal (1,000 gp)",
        "Star Ruby (1,000 gp)", "Star Sapphire (1,000 gp)",
    ],
    "legendary": [
        "Black Sapphire (5,000 gp)", "Diamond (5,000 gp)",
        "Jacinth (5,000 gp)", "Ruby (5,000 gp)", "Oriental Emerald (5,000 gp)",
    ],
}

MAGIC_ITEMS = {
    "common": [
        "Potion of Healing", "Potion of Climbing", "Spell Scroll (Cantrip)",
        "Spell Scroll (1st Level)", "Bag of Tricks", "Candle of the Deep",
        "Cloak of Billowing",
    ],
    "uncommon": [
        "Potion of Greater Healing", "Potion of Fire Breath", "+1 Weapon",
        "Ring of Swimming", "Wand of Magic Detection", "Cloak of Protection",
        "Boots of Elvenkind", "Goggles of Night", "Rope of Climbing",
        "Staff of the Adder", "Wand of Secrets",
    ],
    "rare": [
        "Potion of Superior Healing", "+2 Weapon", "Staff of Charming",
        "Ring of Protection", "Amulet of Health", "Flame Tongue",
        "Wand of Fireballs", "Wand of Lightning Bolts", "Staff of Healing",
        "Ring of Spell Storing", "Necklace of Fireballs",
    ],
    "very_rare": [
        "Potion of Supreme Healing", "+3 Weapon", "Staff of Power",
        "Ring of Regeneration", "Belt of Fire Giant Strength",
        "Cloak of Invisibility", "Rod of Absorption", "Crystal Ball",
    ],
    "legendary": [
        "Vorpal Sword", "Sphere of Annihilation", "Staff of the Magi",
        "Holy Avenger", "Luck Blade", "Ring of Three Wishes",
    ],
}


def _roll(count: int, sides: int) -> int:
    return sum(random.randint(1, sides) for _ in range(count))


def _pick(pool: list, count: int) -> list:
    return random.sample(pool, min(count, len(pool)))


def generate_treasure(max_cr: float) -> dict:
    coins: dict[str, int] = {}
    gems: list[str] = []
    magic_items: list[str] = []

    if max_cr <= 4:
        tier = "Low"
        cp = _roll(5, 6) * 100
        sp = _roll(4, 6) * 10
        gp = _roll(3, 6)
        if cp: coins["Copper"] = cp
        if sp: coins["Silver"] = sp
        if gp: coins["Gold"] = gp
        if random.random() < 0.30:
            gems = _pick(GEMS["low"], random.randint(1, 3))
        r = random.random()
        if r < 0.10:
            magic_items = _pick(MAGIC_ITEMS["common"], 1)

    elif max_cr <= 10:
        tier = "Medium"
        gp = _roll(4, 6) * 10
        pp = _roll(1, 6) * 5
        if gp: coins["Gold"] = gp
        if pp: coins["Platinum"] = pp
        if random.random() < 0.40:
            gems = _pick(GEMS["low"] + GEMS["mid"], random.randint(1, 4))
        r = random.random()
        if r < 0.05:
            magic_items = _pick(MAGIC_ITEMS["rare"], 1)
        elif r < 0.30:
            magic_items = _pick(MAGIC_ITEMS["uncommon"], 1)
        elif r < 0.50:
            magic_items = _pick(MAGIC_ITEMS["common"], 1)

    elif max_cr <= 16:
        tier = "High"
        gp = _roll(4, 6) * 100
        pp = _roll(1, 6) * 10
        if gp: coins["Gold"] = gp
        if pp: coins["Platinum"] = pp
        if random.random() < 0.55:
            gems = _pick(GEMS["mid"] + GEMS["high"], random.randint(2, 6))
        r = random.random()
        if r < 0.10:
            magic_items = _pick(MAGIC_ITEMS["very_rare"], random.randint(1, 2))
        elif r < 0.45:
            magic_items = _pick(MAGIC_ITEMS["rare"], 1)
        elif r < 0.70:
            magic_items = _pick(MAGIC_ITEMS["uncommon"], 1)

    else:
        tier = "Legendary"
        gp = _roll(12, 6) * 1000
        pp = _roll(8, 6) * 100
        if gp: coins["Gold"] = gp
        if pp: coins["Platinum"] = pp
        gems = _pick(GEMS["high"] + GEMS["legendary"], random.randint(3, 8))
        r = random.random()
        if r < 0.25:
            magic_items = _pick(MAGIC_ITEMS["legendary"], 1)
        elif r < 0.60:
            magic_items = _pick(MAGIC_ITEMS["very_rare"], random.randint(1, 2))
        else:
            magic_items = _pick(MAGIC_ITEMS["rare"], random.randint(1, 2))

    return {"tier": tier, "coins": coins, "gems": gems, "magic_items": magic_items}
