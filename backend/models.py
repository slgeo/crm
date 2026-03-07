from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    position = Column(String, nullable=True)
    percent = Column(Float, default=40)
    description = Column(String, nullable=True)
    color = Column(String, default="#6366f1")
    default_duration = Column(Integer, default=60)  # минуты
    branch_id = Column(Integer, ForeignKey("branches.id"))
    avatar = Column(String, nullable=True)
    services = relationship("Service", secondary="master_services", back_populates="masters")
    
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    appointment_time = Column(DateTime, default=datetime.utcnow)
    price = Column(Float)
    master_income = Column(Float)
    master_id = Column(Integer, ForeignKey("masters.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    service = relationship("Service")    

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)  # owner / admin / master
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=True)
    
class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    services = relationship("Service", back_populates="category")

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    category_id = Column(Integer, ForeignKey("service_categories.id"))
    category = relationship("ServiceCategory", back_populates="services")

    price = Column(Float, default=0)
    duration_minutes = Column(Integer, default=60)
    masters = relationship("Master", secondary="master_services", back_populates="services")


master_services = Table(
    "master_services",
    Base.metadata,
    Column("master_id", Integer, ForeignKey("masters.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
)

    
