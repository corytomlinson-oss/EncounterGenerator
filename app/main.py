import json
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db, SessionLocal
from app.models import Monster, SavedEncounter
from app.encounter import generate_encounter, DIFFICULTY_LABELS, DIFFICULTY_COLORS, DIFFICULTY_BG
from app.seed import seed_monsters
from app.treasure import generate_treasure

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Monster).count() == 0:
            seed_monsters(db)
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    party_level: int = Form(...),
    party_size: int = Form(...),
    difficulty: str = Form(...),
    num_creatures: int = Form(...),
    encounter_type: str = Form(...),
    environment: str = Form(...),
    include_treasure: str = Form(default=""),
    db: Session = Depends(get_db),
):
    result = generate_encounter(
        party_level=party_level,
        party_size=party_size,
        difficulty=difficulty,
        num_creatures=num_creatures,
        encounter_type=encounter_type,
        environment=environment,
        db=db,
    )
    if not result:
        return HTMLResponse("<p class='text-red-500'>No monsters found for those filters.</p>")

    result["treasure"] = generate_treasure(result["max_cr"]) if include_treasure else None
    return templates.TemplateResponse(request, "partials/encounter_result.html", result)


@app.post("/save", response_class=HTMLResponse)
def save_encounter(
    request: Request,
    name: str = Form(""),
    party_level: int = Form(...),
    party_size: int = Form(...),
    difficulty: str = Form(...),
    environment: str = Form(...),
    encounter_type: str = Form(...),
    monster_ids: str = Form(...),
    raw_xp: int = Form(...),
    adjusted_xp: int = Form(...),
    actual_difficulty: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    ids = [int(i) for i in monster_ids.split(",") if i.strip()]
    monsters = [db.query(Monster).get(i) for i in ids]
    monsters_data = [m.to_dict() for m in monsters if m]

    enc = SavedEncounter(
        name=name or None,
        party_level=party_level,
        party_size=party_size,
        difficulty=difficulty,
        environment=environment,
        encounter_type=encounter_type,
        monsters_json=json.dumps(monsters_data),
        total_xp=raw_xp,
        adjusted_xp=adjusted_xp,
        actual_difficulty=actual_difficulty,
        notes=notes or None,
    )
    db.add(enc)
    db.commit()
    return HTMLResponse(
        "<p class='text-green-600 font-medium'>Encounter saved!</p>"
    )


@app.get("/history", response_class=HTMLResponse)
def history(request: Request, db: Session = Depends(get_db)):
    encounters = db.query(SavedEncounter).order_by(SavedEncounter.created_at.desc()).all()
    return templates.TemplateResponse(request, "history.html", {"encounters": encounters})


@app.get("/history/{enc_id}", response_class=HTMLResponse)
def history_detail(enc_id: int, request: Request, db: Session = Depends(get_db)):
    enc = db.query(SavedEncounter).get(enc_id)
    if not enc:
        return HTMLResponse("<p>Not found.</p>", status_code=404)
    return templates.TemplateResponse(request, "history_detail.html", {"enc": enc})


@app.post("/history/{enc_id}/delete", response_class=HTMLResponse)
def delete_encounter(enc_id: int, db: Session = Depends(get_db)):
    enc = db.query(SavedEncounter).get(enc_id)
    if enc:
        db.delete(enc)
        db.commit()
    return HTMLResponse("")
