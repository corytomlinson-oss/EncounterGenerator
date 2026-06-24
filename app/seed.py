import json
import os
from sqlalchemy.orm import Session
from app.models import Monster


def seed_monsters(db: Session) -> None:
    path = os.path.join(os.path.dirname(__file__), "data", "monsters.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for m in data:
        monster = Monster(
            name       = m["name"],
            cr         = m["cr"],
            xp         = m["xp"],
            size       = m["size"],
            type       = m["type"],
            subtype    = m.get("subtype"),
            alignment  = m["alignment"],
            ac         = m["ac"],
            ac_note    = m.get("ac_note"),
            hp         = m["hp"],
            hp_dice    = m.get("hp_dice"),
            speed      = m["speed"],
            str_       = m["str"],
            dex        = m["dex"],
            con        = m["con"],
            int_       = m["int"],
            wis        = m["wis"],
            cha        = m["cha"],
            saving_throws         = json.dumps(m.get("saving_throws", {})),
            skills                = json.dumps(m.get("skills", {})),
            damage_vulnerabilities = m.get("damage_vulnerabilities"),
            damage_resistances    = m.get("damage_resistances"),
            damage_immunities     = m.get("damage_immunities"),
            condition_immunities  = m.get("condition_immunities"),
            senses     = m.get("senses"),
            languages  = m.get("languages"),
            special_abilities = json.dumps(m.get("special_abilities", [])),
            actions           = json.dumps(m.get("actions", [])),
            reactions         = json.dumps(m.get("reactions", [])),
            legendary_desc    = m.get("legendary_desc"),
            legendary_actions = json.dumps(m.get("legendary_actions", [])),
            environments = m.get("environments", ""),
            image_url    = m.get("image_url"),
        )
        db.add(monster)

    db.commit()
    print(f"[seed] {len(data)} monsters loaded.")
