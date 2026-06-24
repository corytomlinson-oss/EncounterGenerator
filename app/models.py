import json
from datetime import datetime
from collections import Counter
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from app.database import Base


class Monster(Base):
    __tablename__ = "monsters"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(200), nullable=False, index=True)
    cr         = Column(Float, nullable=False, index=True)
    xp         = Column(Integer, nullable=False)
    size       = Column(String(20), nullable=False)
    type       = Column(String(50), nullable=False, index=True)
    subtype    = Column(String(100), nullable=True)
    alignment  = Column(String(100), nullable=False)
    ac         = Column(Integer, nullable=False)
    ac_note    = Column(String(150), nullable=True)
    hp         = Column(Integer, nullable=False)
    hp_dice    = Column(String(50), nullable=True)
    speed      = Column(String(100), nullable=False)
    str_       = Column("str", Integer, nullable=False)
    dex        = Column(Integer, nullable=False)
    con        = Column(Integer, nullable=False)
    int_       = Column("int", Integer, nullable=False)
    wis        = Column(Integer, nullable=False)
    cha        = Column(Integer, nullable=False)
    saving_throws         = Column(Text, nullable=True)  # JSON {"WIS": "+4"}
    skills                = Column(Text, nullable=True)  # JSON {"Stealth": "+6"}
    damage_vulnerabilities = Column(String(300), nullable=True)
    damage_resistances    = Column(String(300), nullable=True)
    damage_immunities     = Column(String(300), nullable=True)
    condition_immunities  = Column(String(300), nullable=True)
    senses     = Column(String(250), nullable=True)
    languages  = Column(String(250), nullable=True)
    special_abilities = Column(Text, nullable=True)  # JSON [{name, desc}]
    actions           = Column(Text, nullable=True)  # JSON [{name, desc}]
    reactions         = Column(Text, nullable=True)  # JSON [{name, desc}]
    legendary_desc    = Column(Text, nullable=True)
    legendary_actions = Column(Text, nullable=True)  # JSON [{name, desc}]
    environments = Column(String(300), nullable=True)  # comma-separated
    image_url    = Column(String(500), nullable=True)

    # ── display helpers ────────────────────────────────────────────────────────
    @property
    def cr_display(self):
        if self.cr == 0:     return "0"
        if self.cr == 0.125: return "1/8"
        if self.cr == 0.25:  return "1/4"
        if self.cr == 0.5:   return "1/2"
        return str(int(self.cr))

    def _mod(self, score): return (score - 10) // 2
    def _fmt(self, m):     return f"+{m}" if m >= 0 else str(m)

    @property
    def str_mod(self): return self._mod(self.str_)
    @property
    def dex_mod(self): return self._mod(self.dex)
    @property
    def con_mod(self): return self._mod(self.con)
    @property
    def int_mod(self): return self._mod(self.int_)
    @property
    def wis_mod(self): return self._mod(self.wis)
    @property
    def cha_mod(self): return self._mod(self.cha)

    @property
    def str_mod_fmt(self): return self._fmt(self.str_mod)
    @property
    def dex_mod_fmt(self): return self._fmt(self.dex_mod)
    @property
    def con_mod_fmt(self): return self._fmt(self.con_mod)
    @property
    def int_mod_fmt(self): return self._fmt(self.int_mod)
    @property
    def wis_mod_fmt(self): return self._fmt(self.wis_mod)
    @property
    def cha_mod_fmt(self): return self._fmt(self.cha_mod)

    @property
    def saving_throws_dict(self): return json.loads(self.saving_throws) if self.saving_throws else {}
    @property
    def skills_dict(self):        return json.loads(self.skills) if self.skills else {}

    @property
    def all_saving_throws(self):
        """All 6 saves: proficiency override (from saving_throws_dict) or base ability modifier."""
        prof = {k.upper(): v for k, v in self.saving_throws_dict.items()}
        base = {
            "STR": self._fmt(self.str_mod),
            "DEX": self._fmt(self.dex_mod),
            "CON": self._fmt(self.con_mod),
            "INT": self._fmt(self.int_mod),
            "WIS": self._fmt(self.wis_mod),
            "CHA": self._fmt(self.cha_mod),
        }
        return {stat: (prof[stat], True) if stat in prof else (base[stat], False)
                for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA")}
    @property
    def special_abilities_list(self): return json.loads(self.special_abilities) if self.special_abilities else []
    @property
    def actions_list(self):           return json.loads(self.actions) if self.actions else []
    @property
    def reactions_list(self):         return json.loads(self.reactions) if self.reactions else []
    @property
    def legendary_actions_list(self): return json.loads(self.legendary_actions) if self.legendary_actions else []

    @property
    def type_color(self):
        colors = {
            "beast": "bg-green-100 text-green-800",
            "humanoid": "bg-blue-100 text-blue-800",
            "undead": "bg-purple-100 text-purple-800",
            "fiend": "bg-red-100 text-red-800",
            "elemental": "bg-orange-100 text-orange-800",
            "giant": "bg-yellow-100 text-yellow-800",
            "dragon": "bg-rose-100 text-rose-800",
            "monstrosity": "bg-amber-100 text-amber-800",
            "ooze": "bg-lime-100 text-lime-800",
            "plant": "bg-emerald-100 text-emerald-800",
            "fey": "bg-pink-100 text-pink-800",
            "construct": "bg-gray-100 text-gray-800",
            "aberration": "bg-violet-100 text-violet-800",
            "celestial": "bg-sky-100 text-sky-800",
        }
        return colors.get(self.type, "bg-stone-100 text-stone-800")

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "cr": self.cr,
            "cr_display": self.cr_display, "xp": self.xp,
            "size": self.size, "type": self.type, "subtype": self.subtype,
            "alignment": self.alignment, "ac": self.ac, "ac_note": self.ac_note,
            "hp": self.hp, "hp_dice": self.hp_dice, "speed": self.speed,
            "str": self.str_, "dex": self.dex, "con": self.con,
            "int": self.int_, "wis": self.wis, "cha": self.cha,
            "str_mod": self.str_mod, "dex_mod": self.dex_mod, "con_mod": self.con_mod,
            "int_mod": self.int_mod, "wis_mod": self.wis_mod, "cha_mod": self.cha_mod,
            "str_mod_fmt": self.str_mod_fmt, "dex_mod_fmt": self.dex_mod_fmt,
            "con_mod_fmt": self.con_mod_fmt, "int_mod_fmt": self.int_mod_fmt,
            "wis_mod_fmt": self.wis_mod_fmt, "cha_mod_fmt": self.cha_mod_fmt,
            "saving_throws": self.saving_throws_dict,
            "all_saving_throws": {k: {"val": v, "prof": p} for k, (v, p) in self.all_saving_throws.items()},
            "skills": self.skills_dict,
            "damage_vulnerabilities": self.damage_vulnerabilities,
            "damage_resistances": self.damage_resistances,
            "damage_immunities": self.damage_immunities,
            "condition_immunities": self.condition_immunities,
            "senses": self.senses, "languages": self.languages,
            "special_abilities": self.special_abilities_list,
            "actions": self.actions_list, "reactions": self.reactions_list,
            "legendary_desc": self.legendary_desc,
            "legendary_actions": self.legendary_actions_list,
            "environments": self.environments, "image_url": self.image_url,
            "type_color": self.type_color,
        }


class SavedEncounter(Base):
    __tablename__ = "saved_encounters"

    id               = Column(Integer, primary_key=True, index=True)
    name             = Column(String(200), nullable=True)
    party_level      = Column(Integer, nullable=False)
    party_size       = Column(Integer, nullable=False)
    difficulty       = Column(String(20), nullable=False)
    environment      = Column(String(50), nullable=True)
    encounter_type   = Column(String(20), nullable=False)
    monsters_json    = Column(Text, nullable=False)
    total_xp         = Column(Integer, nullable=False)
    adjusted_xp      = Column(Integer, nullable=False)
    actual_difficulty = Column(String(20), nullable=False)
    notes            = Column(Text, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    @property
    def monsters_list(self):
        return json.loads(self.monsters_json)

    @property
    def monster_summary(self):
        counts = Counter(m["name"] for m in self.monsters_list)
        return ", ".join(
            f"{n}× {name}" if n > 1 else name
            for name, n in counts.items()
        )

    @property
    def difficulty_color(self):
        return {
            "trivial": "text-gray-500",
            "easy":    "text-green-600",
            "medium":  "text-yellow-600",
            "hard":    "text-orange-600",
            "deadly":  "text-red-600",
        }.get(self.actual_difficulty, "text-gray-600")
