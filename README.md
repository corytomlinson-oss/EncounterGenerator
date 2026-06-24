# D&D 5e Encounter Generator

A self-hosted web app for building balanced D&D 5e random encounters by party level, difficulty, and environment. Part of the HomeHub suite running on a Raspberry Pi.

## Features

- XP budget encounter building using DMG thresholds (compatible with 2024 rules)
- Filter monsters by environment (dungeon, forest, cave, mountain, arctic, desert, urban, swamp, coastal)
- Single-type encounters (all same monster) or mixed encounters (horde + boss style with natural duplicates)
- Per-instance HP tracking with bloodied (≤50% HP) and dead states — no page reload needed
- Letter labels for duplicate monsters: Goblin (A), Goblin (B), etc.
- Full stat blocks with ability scores, saving throws, actions, traits, and legendary actions
- Optional treasure generation scaled to the encounter's CR tier (coins, gems, magic items)
- Save encounters to history with optional name and notes
- Browse and delete saved encounters

## Monster Data

84 SRD monsters covering CR 0 through CR 24, seeded from `app/data/monsters.json` into SQLite on first startup.

## Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI + SQLAlchemy (SQLite) |
| Templates | Jinja2 |
| Frontend | HTMX + Alpine.js + Tailwind CSS (all CDN) |
| Server | Uvicorn |

Zero build step — no Node, no bundler.

## Project Structure

```
EncounterGenerator/
├── app/
│   ├── data/
│   │   └── monsters.json       # 84 SRD monsters, CR 0–24
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── history.html
│   │   ├── history_detail.html
│   │   └── partials/
│   │       └── encounter_result.html
│   ├── database.py             # SQLite engine + session
│   ├── encounter.py            # XP budget logic + monster selection
│   ├── main.py                 # FastAPI routes
│   ├── models.py               # Monster + SavedEncounter ORM models
│   ├── seed.py                 # Loads monsters.json into DB on startup
│   └── treasure.py             # CR-tiered treasure table generation
├── systemd/
│   └── encounter-generator.service
├── requirements.txt
└── .gitignore
```

## Local Development

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8084
```

Visit `http://localhost:8084`

## Deployment (Raspberry Pi)

The app runs as a systemd service on `webpi.local` at port 8084. Deploy by copying files via SCP — the Pi has no GitHub credentials so `git pull` does not work there.

```bash
# From Windows dev machine
scp -r app/ requirements.txt cory@webpi.local:/home/cory/HomeHub/EncounterGenerator/
ssh cory@webpi.local "sudo systemctl restart encounter-generator"
```

### First-time Pi setup

```bash
cd /home/cory/HomeHub/EncounterGenerator
python3 -m venv venv
venv/bin/pip install -r requirements.txt

sudo cp systemd/encounter-generator.service /etc/systemd/system/
sudo systemctl enable encounter-generator
sudo systemctl start encounter-generator
```

The database is created automatically at `data/encounter.db` and seeded with monsters on first run.

## Encounter XP Logic

1. Look up XP threshold for the party level + requested difficulty (DMG table)
2. Multiply threshold × party size → XP budget
3. Divide budget by (number of creatures × encounter multiplier) → target XP per creature
4. Select monsters closest to that target XP from the filtered pool
5. Sum raw XP, apply multiplier → adjusted XP
6. Compare adjusted XP against thresholds to determine actual difficulty

Encounter multipliers (DMG): 1 creature ×1.0, 2 ×1.5, 3–6 ×2.0, 7–10 ×2.5, 11–14 ×3.0, 15+ ×4.0

## Treasure Generation

When "Generate Treasure" is checked, the app rolls a hoard appropriate to the highest CR monster in the encounter:

| CR Range | Tier | Coins | Gems | Magic Items |
|----------|------|-------|------|-------------|
| 0–4 | Low | cp / sp / gp | 30% chance, 10 gp gems | 10% common |
| 5–10 | Medium | gp / pp | 40% chance, 50–100 gp gems | 30% uncommon, 5% rare |
| 11–16 | High | gp / pp | 55% chance, 500–1,000 gp gems | 45% rare, 10% very rare |
| 17+ | Legendary | gp / pp | Always, 1,000–5,000 gp gems | Always rare or higher |
