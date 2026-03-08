from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models
from datetime import datetime
import re

Base.metadata.create_all(bind=engine)

app = FastAPI()


PHONE_REGEX = re.compile(r"^\+7\d{10}$")
APPOINTMENT_STATUSES = {"waiting", "arrived", "absent", "confirmed"}


def normalize_phone(phone: str | None):
    if phone is None:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits[0] in {"7", "8"}:
        digits = "7" + digits[1:]
    elif len(digits) == 10:
        digits = "7" + digits
    if len(digits) != 11 or not digits.startswith("7"):
        return None
    return f"+{digits}"


def validate_phone(phone: str | None):
    normalized = normalize_phone(phone)
    if not normalized or not PHONE_REGEX.match(normalized):
        raise HTTPException(status_code=400, detail="Phone must be in +7XXXXXXXXXX format")
    return normalized


def serialize_client(client: models.Client):
    return {
        "id": client.id,
        "name": client.name,
        "phone": client.phone,
        "email": client.email
    }


def get_or_create_client(db: Session, client_name: str | None, client_phone: str | None):
    if not client_phone:
        return None

    normalized_phone = validate_phone(client_phone)
    client = db.query(models.Client).filter(models.Client.phone == normalized_phone).first()
    clean_name = (client_name or "").strip()

    if client:
        if clean_name:
            client.name = clean_name
        return client

    client = models.Client(
        name=clean_name or "Новый клиент",
        phone=normalized_phone
    )
    db.add(client)
    db.flush()
    return client

def serialize_master(master: models.Master):
    return {
        "id": master.id,
        "name": master.name,
        "phone": master.phone,
        "email": master.email,
        "position": master.position,
        "percent": master.percent,
        "description": master.description,
        "color": master.color,
        "default_duration": master.default_duration,
        "branch_id": master.branch_id,
        "avatar": master.avatar,
        "service_ids": [service.id for service in master.services]
    }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- МАСТЕРА -------------------

@app.get("/api/positions")
def get_positions(db: Session = Depends(get_db)):
    return db.query(models.Position).all()


@app.post("/api/positions")
def create_position(data: dict, db: Session = Depends(get_db)):
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Position name is required")

    position = models.Position(
        name=name,
        description=data.get("description")
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return position


@app.delete("/api/positions/{position_id}")
def delete_position(position_id: int, db: Session = Depends(get_db)):
    position = db.query(models.Position).get(position_id)
    if not position:
        raise HTTPException(status_code=404)

    db.delete(position)
    db.commit()
    return {"message": "Deleted"}


@app.put("/api/positions/{position_id}")
def update_position(position_id: int, data: dict, db: Session = Depends(get_db)):
    position = db.query(models.Position).get(position_id)
    if not position:
        raise HTTPException(status_code=404)

    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Position name is required")

    position.name = name
    position.description = data.get("description")

    db.commit()
    db.refresh(position)
    return position

@app.get("/api/masters")
def get_masters(db: Session = Depends(get_db)):
    masters = db.query(models.Master).all()
    return [serialize_master(master) for master in masters]

@app.post("/api/masters")
def create_master(data: dict, db: Session = Depends(get_db)):
    service_ids = data.get("service_ids", [])
    services = []
    if service_ids:
        services = db.query(models.Service).filter(models.Service.id.in_(service_ids)).all()

    master = models.Master(
        name=data["name"],
        phone=data.get("phone"),
        email=data.get("email"),
        position=data.get("position"),
        percent=data.get("percent", 40),
        description=data.get("description"),
        color=data.get("color", "#6366f1"),
        default_duration=data.get("default_duration", 60),
        avatar=data.get("avatar")
    )
    master.services = services
    db.add(master)
    db.commit()
    db.refresh(master)
    return serialize_master(master)
    
@app.put("/api/masters/{master_id}")
def update_master(master_id: int, data: dict, db: Session = Depends(get_db)):
    master = db.query(models.Master).get(master_id)
    if not master:
        raise HTTPException(status_code=404)

    master.name = data.get("name")
    service_ids = data.get("service_ids", [])
    services = []
    if service_ids:
        services = db.query(models.Service).filter(models.Service.id.in_(service_ids)).all()

    master.phone = data.get("phone")
    master.email = data.get("email")
    master.position = data.get("position")
    master.percent = data.get("percent")
    master.color = data.get("color")
    master.avatar = data.get("avatar")
    master.services = services

    db.commit()
    db.refresh(master)
    return serialize_master(master)

@app.delete("/api/masters/{master_id}")
def delete_master(master_id: int, db: Session = Depends(get_db)):
    master = db.query(models.Master).get(master_id)
    if not master:
        raise HTTPException(status_code=404)

    db.delete(master)
    db.commit()
    return {"message": "Deleted"}    
# ------------------- ЗАПИСИ -------------------

@app.get("/api/services")
def get_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()


@app.get("/api/service-categories")
def get_service_categories(db: Session = Depends(get_db)):
    return db.query(models.ServiceCategory).all()


@app.post("/api/service-categories")
def create_service_category(data: dict, db: Session = Depends(get_db)):
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Category name is required")

    category = models.ServiceCategory(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.delete("/api/service-categories/{category_id}")
def delete_service_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.ServiceCategory).get(category_id)
    if not category:
        raise HTTPException(status_code=404)

    services_count = db.query(models.Service).filter(models.Service.category_id == category_id).count()
    if services_count:
        raise HTTPException(status_code=400, detail="Category is used in services")

    db.delete(category)
    db.commit()
    return {"message": "Deleted"}


@app.put("/api/service-categories/{category_id}")
def update_service_category(category_id: int, data: dict, db: Session = Depends(get_db)):
    category = db.query(models.ServiceCategory).get(category_id)
    if not category:
        raise HTTPException(status_code=404)

    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Category name is required")

    category.name = name

    db.commit()
    db.refresh(category)
    return category


@app.post("/api/services")
def create_service(data: dict, db: Session = Depends(get_db)):
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Service name is required")

    category_id = data.get("category_id")
    if category_id:
        category = db.query(models.ServiceCategory).get(category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    service = models.Service(
        name=name,
        category_id=category_id,
        price=data.get("price", 0),
        duration_minutes=data.get("duration_minutes", 60)
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@app.put("/api/services/{service_id}")
def update_service(service_id: int, data: dict, db: Session = Depends(get_db)):
    service = db.query(models.Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404)

    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Service name is required")

    category_id = data.get("category_id")
    if category_id:
        category = db.query(models.ServiceCategory).get(category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    service.name = name
    service.category_id = category_id
    service.price = data.get("price", 0)
    service.duration_minutes = data.get("duration_minutes", 60)

    db.commit()
    db.refresh(service)
    return service


@app.delete("/api/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404)

    db.delete(service)
    db.commit()
    return {"message": "Deleted"}


# ------------------- CLIENTS -------------------

@app.get("/api/clients")
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(models.Client).order_by(models.Client.name.asc()).all()
    return [serialize_client(client) for client in clients]


@app.get("/api/clients/find-by-phone")
def find_client_by_phone(phone: str = Query(...), db: Session = Depends(get_db)):
    normalized_phone = normalize_phone(phone)
    if not normalized_phone:
        return None

    client = db.query(models.Client).filter(models.Client.phone == normalized_phone).first()
    if not client:
        return None

    return serialize_client(client)


@app.post("/api/clients")
def create_client(data: dict, db: Session = Depends(get_db)):
    phone = validate_phone(data.get("phone"))

    existing = db.query(models.Client).filter(models.Client.phone == phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Client with this phone already exists")

    client = models.Client(
        name=(data.get("name") or "").strip() or "Новый клиент",
        phone=phone,
        email=(data.get("email") or "").strip() or None
    )

    db.add(client)
    db.commit()
    db.refresh(client)
    return serialize_client(client)


@app.put("/api/clients/{client_id}")
def update_client(client_id: int, data: dict, db: Session = Depends(get_db)):
    client = db.query(models.Client).get(client_id)
    if not client:
        raise HTTPException(status_code=404)

    phone = validate_phone(data.get("phone"))

    existing = db.query(models.Client).filter(models.Client.phone == phone, models.Client.id != client_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Client with this phone already exists")

    client.name = (data.get("name") or "").strip() or "Новый клиент"
    client.phone = phone
    client.email = (data.get("email") or "").strip() or None

    db.commit()
    db.refresh(client)
    return serialize_client(client)


@app.delete("/api/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).get(client_id)
    if not client:
        raise HTTPException(status_code=404)

    db.delete(client)
    db.commit()
    return {"message": "Deleted"}

# ------------------- ЗАПИСИ -------------------

@app.get("/api/appointments")
def get_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()

@app.post("/api/appointments")
def create_appointment(data: dict, db: Session = Depends(get_db)):
    status = data.get("status", "waiting")
    if status not in APPOINTMENT_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid appointment status")

    client = get_or_create_client(
        db,
        data.get("client_name"),
        data.get("client_phone")
    )

    appt = models.Appointment(
        title=data["title"],
        appointment_time=datetime.fromisoformat(data["datetime"]),
        master_id=data.get("master_id"),
        service_id=data.get("service_id"),
        status=status,
        client_id=client.id if client else None,
        price=data.get("price", 0),
        master_income=data.get("master_income", 0)
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt
    
@app.put("/api/appointments/{appt_id}")
def update_appointment(appt_id: int, data: dict, db: Session = Depends(get_db)):
    appt = db.query(models.Appointment).get(appt_id)
    if not appt:
        raise HTTPException(status_code=404)

    status = data.get("status", appt.status or "waiting")
    if status not in APPOINTMENT_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid appointment status")

    client = get_or_create_client(
        db,
        data.get("client_name"),
        data.get("client_phone")
    )

    appt.title = data["title"]
    appt.price = data.get("price", 0)
    appt.master_id = data.get("master_id")
    appt.service_id = data.get("service_id")
    appt.status = status
    appt.client_id = client.id if client else appt.client_id
    appt.appointment_time = datetime.fromisoformat(data["datetime"])

    db.commit()
    return appt
    
@app.delete("/api/appointments/{appt_id}")
def delete_appointment(appt_id: int, db: Session = Depends(get_db)):
    appt = db.query(models.Appointment).get(appt_id)
    if not appt:
        raise HTTPException(status_code=404)
    db.delete(appt)
    db.commit()
    return {"status": "deleted"}
