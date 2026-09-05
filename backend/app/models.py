from enum import Enum

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


user_roles = Table(
    "user_roles", Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions", Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    is_system_role: Mapped[bool] = mapped_column(default=True, nullable=False)
    users: Mapped[list["User"]] = relationship(secondary=user_roles, back_populates="roles")
    permissions: Mapped[list["Permission"]] = relationship(secondary=role_permissions, back_populates="roles")


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    scope: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    roles: Mapped[list[Role]] = relationship(secondary=role_permissions, back_populates="permissions")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    profile_completed: Mapped[bool] = mapped_column(default=True, nullable=False)
    employee_id: Mapped[str | None] = mapped_column(ForeignKey("employees.id"), unique=True, nullable=True)
    roles: Mapped[list[Role]] = relationship(secondary=user_roles, back_populates="users")
    employee: Mapped["Employee | None"] = relationship()


class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    AVAILABLE_RETURN = "AVAILABLE_RETURN"
    NOT_READY = "NOT_READY"
    MAINTENANCE = "MAINTENANCE"


class JobSource(str, Enum):
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"


class JobType(str, Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class JobStatus(str, Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


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


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    source: Mapped[JobSource] = mapped_column(default=JobSource.EXTERNAL, nullable=False)
    origin: Mapped[str] = mapped_column(String(120), nullable=False)
    destination: Mapped[str] = mapped_column(String(120), nullable=False)
    pickup_date: Mapped[str] = mapped_column(String(20), nullable=False)
    pickup_time: Mapped[str] = mapped_column(String(10), nullable=False)
    customer_reference: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    job_type: Mapped[JobType] = mapped_column(default=JobType.ONE_WAY, nullable=False)
    status: Mapped[JobStatus] = mapped_column(default=JobStatus.CREATED, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
