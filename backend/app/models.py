from enum import Enum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    AVAILABLE_RETURN = "AVAILABLE_RETURN"
    NOT_READY = "NOT_READY"
    MAINTENANCE = "MAINTENANCE"


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False, default="DRIVER")
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    vehicle: Mapped["Vehicle | None"] = relationship(back_populates="employee", uselist=False)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    plate: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    employee_id: Mapped[str | None] = mapped_column(ForeignKey("employees.id"), nullable=True)
    status: Mapped[VehicleStatus] = mapped_column(default=VehicleStatus.NOT_READY)
    ready_from: Mapped[str | None] = mapped_column(String(120), nullable=True)
    current_destination: Mapped[str | None] = mapped_column(String(120), nullable=True)
    employee: Mapped[Employee | None] = relationship(back_populates="vehicle")
