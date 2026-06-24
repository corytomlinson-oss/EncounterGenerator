import random
import string
from collections import Counter
from sqlalchemy.orm import Session
from app.models import Monster

# XP thresholds per character by level (5e DMG, compatible with 2024 rules)
XP_THRESHOLDS = {
    1:  {"easy": 25,   "medium": 50,   "hard": 75,    "deadly": 100},
    2:  {"easy": 50,   "medium": 100,  "hard": 150,   "deadly": 200},
    3:  {"easy": 75,   "medium": 150,  "hard": 225,   "deadly": 400},
    4:  {"easy": 125,  "medium": 250,  "hard": 375,   "deadly": 500},
    5:  {"easy": 250,  "medium": 500,  "hard": 750,   "deadly": 1100},
    6:  {"easy": 300,  "medium": 600,  "hard": 900,   "deadly": 1400},
    7:  {"easy": 350,  "medium": 750,  "hard": 1100,  "deadly": 1700},
    8:  {"easy": 450,  "medium": 900,  "hard": 1400,  "deadly": 2100},
    9:  {"easy": 550,  "medium": 1100, "hard": 1600,  "deadly": 2400},
    10: {"easy": 600,  "medium": 1200, "hard": 1900,  "deadly": 2800},
    11: {"easy": 800,  "medium": 1600, "hard": 2400,  "deadly": 3600},
    12: {"easy": 1000, "medium": 2000, "hard": 3000,  "deadly": 4500},
    13: {"easy": 1100, "medium": 2200, "hard": 3400,  "deadly": 5100},
    14: {"easy": 1250, "medium": 2500, "hard": 3800,  "deadly": 5700},
    15: {"easy": 1400, "medium": 2800, "hard": 4300,  "deadly": 6400},
    16: {"easy": 1600, "medium": 3200, "hard": 4800,  "deadly": 7200},
    17: {"easy": 2000, "medium": 3900, "hard": 5900,  "deadly": 8800},
    18: {"easy": 2100, "medium": 4200, "hard": 6300,  "deadly": 9500},
    19: {"easy": 2400, "medium": 4900, "hard": 7300,  "deadly": 10900},
    20: {"easy": 2800, "medium": 5700, "hard": 8500,  "deadly": 12700},
}

DIFFICULTY_LABELS = {
    "easy": "Easy", "medium": "Medium", "hard": "Hard", "deadly": "Deadly", "trivial": "Trivial"
}

DIFFICULTY_COLORS = {
    "trivial": "text-gray-400",
    "easy":    "text-green-500",
    "medium":  "text-yellow-500",
    "hard":    "text-orange-500",
    "deadly":  "text-red-500",
}

DIFFICULTY_BG = {
    "trivial": "bg-gray-100 text-gray-700",
    "easy":    "bg-green-100 text-green-800",
    "medium":  "bg-yellow-100 text-yellow-800",
    "hard":    "bg-orange-100 text-orange-800",
    "deadly":  "bg-red-100 text-red-800",
}


def get_multiplier(n: int) -> float:
    if n == 1:  return 1.0
    if n == 2:  return 1.5
    if n <= 6:  return 2.0
    if n <= 10: return 2.5
    if n <= 14: return 3.0
    return 4.0


def get_actual_difficulty(adjusted_xp: int, party_level: int, party_size: int) -> str:
    t = XP_THRESHOLDS.get(party_level, XP_THRESHOLDS[20])
    if adjusted_xp < t["easy"]   * party_size: return "trivial"
    if adjusted_xp < t["medium"] * party_size: return "easy"
    if adjusted_xp < t["hard"]   * party_size: return "medium"
    if adjusted_xp < t["deadly"] * party_size: return "hard"
    return "deadly"


def _get_pool(environment: str, db: Session):
    q = db.query(Monster)
    if environment and environment != "random":
        q = q.filter(Monster.environments.like(f"%{environment}%"))
    pool = q.all()
    if not pool:
        pool = db.query(Monster).all()
    return pool


def _pick_closest(pool, target_xp: float) -> Monster:
    return min(pool, key=lambda m: abs(m.xp - target_xp))


def _compute_instance_meta(selected: list) -> tuple:
    """Returns (labels, unique_monsters, instance_to_unique_index)."""
    name_counts = Counter(m.name for m in selected)
    name_letter_idx: dict[str, int] = {}
    labels = []
    for m in selected:
        if name_counts[m.name] > 1:
            idx = name_letter_idx.get(m.name, 0)
            labels.append(string.ascii_uppercase[min(idx, 25)])
            name_letter_idx[m.name] = idx + 1
        else:
            labels.append("")

    seen: dict[str, int] = {}
    unique_monsters = []
    instance_to_unique = []
    for m in selected:
        if m.name not in seen:
            seen[m.name] = len(unique_monsters)
            unique_monsters.append(m)
        instance_to_unique.append(seen[m.name])

    return labels, unique_monsters, instance_to_unique


def _pick_mixed(pool, target_xp: float, num: int) -> list:
    """
    Horde+boss weighting: pick 1-2 higher-CR anchors, then fill remaining
    slots with multiples of a lower-CR creature. Produces encounters like
    '5 Goblins + 1 Orc' rather than all-unique monsters.
    """
    if num <= 2:
        # Too few to do horde logic; just pick diverse creatures
        result, used = [], set()
        for _ in range(num):
            lo, hi = target_xp * 0.35, target_xp * 2.0
            candidates = [m for m in pool if lo <= m.xp <= hi]
            if not candidates:
                candidates = sorted(pool, key=lambda m: abs(m.xp - target_xp))[:6]
            unused = [m for m in candidates if m.name not in used]
            chosen = random.choice(unused if unused else candidates)
            result.append(chosen)
            used.add(chosen.name)
        return result

    # Pick 1 anchor (boss-tier): target_xp * 2–4x
    boss_candidates = [m for m in pool if target_xp * 1.5 <= m.xp <= target_xp * 5.0]
    if not boss_candidates:
        boss_candidates = sorted(pool, key=lambda m: abs(m.xp - target_xp * 2.5))[:4]
    boss = random.choice(boss_candidates)

    # Horde filler: target_xp * 0.2–0.6x (noticeably weaker than boss)
    horde_candidates = [m for m in pool if target_xp * 0.15 <= m.xp <= target_xp * 0.65
                        and m.name != boss.name]
    if not horde_candidates:
        horde_candidates = [m for m in pool if m.name != boss.name] or pool[:]
    filler = random.choice(horde_candidates)

    # Build result: 1 boss + (num-1) copies of filler
    result = [boss] + [filler] * (num - 1)
    random.shuffle(result)
    return result


def generate_encounter(
    party_level: int,
    party_size: int,
    difficulty: str,
    num_creatures: int,
    encounter_type: str,
    environment: str,
    db: Session,
) -> dict | None:
    level   = max(1, min(20, party_level))
    size    = max(1, min(10, party_size))
    num     = max(1, min(15, num_creatures))
    diff    = difficulty if difficulty in XP_THRESHOLDS[1] else "medium"

    budget     = XP_THRESHOLDS[level][diff] * size
    multiplier = get_multiplier(num)
    target_xp  = budget / (num * multiplier)

    pool = _get_pool(environment, db)
    if not pool:
        return None

    if encounter_type == "single":
        best = _pick_closest(pool, target_xp)
        selected = [best] * num
    else:
        selected = _pick_mixed(pool, target_xp, num)

    raw_xp = sum(m.xp for m in selected)
    adj_xp = int(raw_xp * get_multiplier(len(selected)))
    actual = get_actual_difficulty(adj_xp, level, size)
    labels, unique_monsters, instance_to_unique = _compute_instance_meta(selected)

    return {
        "monsters":            selected,
        "monster_labels":      labels,
        "unique_monsters":     unique_monsters,
        "instance_to_unique":  instance_to_unique,
        "raw_xp":              raw_xp,
        "adjusted_xp":         adj_xp,
        "difficulty":          actual,
        "difficulty_label":    DIFFICULTY_LABELS.get(actual, actual.title()),
        "difficulty_color":    DIFFICULTY_COLORS.get(actual, ""),
        "difficulty_bg":       DIFFICULTY_BG.get(actual, ""),
        "budget":              budget,
        "party_level":         level,
        "party_size":          size,
        "requested_difficulty": diff,
        "encounter_type":      encounter_type,
        "environment":         environment,
        "num_creatures":       num,
    }
