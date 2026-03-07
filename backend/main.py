from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()

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

@app.get("/api/masters")
def get_masters(db: Session = Depends(get_db)):
    return db.query(models.Master).all()

@app.post("/api/masters")
def create_master(data: dict, db: Session = Depends(get_db)):
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
    db.add(master)
    db.commit()
    db.refresh(master)
    return master
    
@app.put("/api/masters/{master_id}")
def update_master(master_id: int, data: dict, db: Session = Depends(get_db)):
    master = db.query(models.Master).get(master_id)
    if not master:
        raise HTTPException(status_code=404)

    master.name = data.get("name")
    master.phone = data.get("phone")
    master.position = data.get("position")
    master.percent = data.get("percent")
    master.color = data.get("color")
    master.avatar = data.get("avatar")

    db.commit()
    db.refresh(master)
    return master 

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

# ------------------- ЗАПИСИ -------------------

@app.get("/api/appointments")
def get_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()

@app.post("/api/appointments")
def create_appointment(data: dict, db: Session = Depends(get_db)):
    appt = models.Appointment(
        title=data["title"],
        appointment_time=datetime.fromisoformat(data["datetime"]),
        master_id=data.get("master_id"),
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

    appt.title = data["title"]
    appt.price = data.get("price", 0)
    appt.master_id = data.get("master_id")
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
