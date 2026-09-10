from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Table, Column, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase): pass

role_permissions = Table("role_permissions", Base.metadata, Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True), Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True))

class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Role(Base, Timestamped):
    __tablename__ = "roles"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="role")
    permissions: Mapped[list["Permission"]] = relationship(secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    scope: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    roles: Mapped[list[Role]] = relationship(secondary=role_permissions, back_populates="permissions")

class User(Base, Timestamped):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), nullable=False)
    employee_id: Mapped[str | None] = mapped_column(ForeignKey("employees.id"), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    profile_completed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    profile_completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
    role: Mapped[Role] = relationship(back_populates="users")
    employee: Mapped["Employee | None"] = relationship(back_populates="user")

class VehicleStatus(str, Enum):
    AVAILABLE="AVAILABLE"; BUSY="BUSY"; AVAILABLE_RETURN="AVAILABLE_RETURN"; NOT_READY="NOT_READY"; MAINTENANCE="MAINTENANCE"
class JobSource(str, Enum): EXTERNAL="EXTERNAL"; INTERNAL="INTERNAL"
class JobType(str, Enum): ONE_WAY="ONE_WAY"; ROUND_TRIP="ROUND_TRIP"
class JobStatus(str, Enum): CREATED="CREATED"; ASSIGNED="ASSIGNED"; IN_PROGRESS="IN_PROGRESS"; COMPLETED="COMPLETED"; CANCELLED="CANCELLED"

class Employee(Base, Timestamped):
    __tablename__="employees"
    id: Mapped[str]=mapped_column(String(20), primary_key=True)
    name: Mapped[str]=mapped_column(String(120), nullable=False)
    position: Mapped[str]=mapped_column(String(50), default="DRIVER", nullable=False)
    phone: Mapped[str]=mapped_column(String(30), nullable=False)
    address: Mapped[str|None]=mapped_column(String(300))
    is_active: Mapped[bool]=mapped_column(Boolean, default=True, nullable=False)
    user: Mapped["User|None"]=relationship(back_populates="employee", uselist=False)
    vehicles: Mapped[list["Vehicle"]]=relationship(back_populates="employee")

class Vehicle(Base, Timestamped):
    __tablename__="vehicles"
    __table_args__=(Index("uq_one_primary_vehicle_per_employee", "employee_id", unique=True, postgresql_where=Column("is_primary") == True),)
    id: Mapped[str]=mapped_column(String(20), primary_key=True)
    plate: Mapped[str]=mapped_column(String(30), unique=True, nullable=False)
    employee_id: Mapped[str]=mapped_column(ForeignKey("employees.id"), nullable=False)
    is_primary: Mapped[bool]=mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[VehicleStatus]=mapped_column(default=VehicleStatus.NOT_READY, nullable=False)
    ready_from: Mapped[str|None]=mapped_column(String(120))
    current_destination: Mapped[str|None]=mapped_column(String(120))
    employee: Mapped[Employee]=relationship(back_populates="vehicles")

class Job(Base, Timestamped):
    __tablename__="jobs"
    id: Mapped[str]=mapped_column(String(30), primary_key=True)
    source: Mapped[JobSource]=mapped_column(default=JobSource.EXTERNAL, nullable=False)
    origin: Mapped[str]=mapped_column(String(120), nullable=False)
    destination: Mapped[str]=mapped_column(String(120), nullable=False)
    pickup_date: Mapped[str]=mapped_column(String(20), nullable=False)
    pickup_time: Mapped[str]=mapped_column(String(10), nullable=False)
    customer_reference: Mapped[str|None]=mapped_column(String(160))
    notes: Mapped[str|None]=mapped_column(String(1000))
    job_type: Mapped[JobType]=mapped_column(default=JobType.ONE_WAY, nullable=False)
    status: Mapped[JobStatus]=mapped_column(default=JobStatus.CREATED, nullable=False)
    driver_id: Mapped[str|None]=mapped_column(ForeignKey("employees.id"))
    vehicle_id: Mapped[str|None]=mapped_column(ForeignKey("vehicles.id"))
    assigned_at: Mapped[datetime|None]=mapped_column(DateTime)
    started_at: Mapped[datetime|None]=mapped_column(DateTime)
    completed_at: Mapped[datetime|None]=mapped_column(DateTime)
    evidences: Mapped[list["JobEvidence"]]=relationship(back_populates="job")

class JobEvidence(Base):
    __tablename__="job_evidences"
    id: Mapped[str]=mapped_column(String(40), primary_key=True)
    job_id: Mapped[str]=mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    uploaded_by_user_id: Mapped[str]=mapped_column(ForeignKey("users.id"), nullable=False)
    file_name: Mapped[str]=mapped_column(String(255), nullable=False)
    file_path: Mapped[str]=mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    job: Mapped[Job]=relationship(back_populates="evidences")

class AuditLog(Base):
    __tablename__="audit_logs"
    id: Mapped[str]=mapped_column(String(40), primary_key=True)
    actor_user_id: Mapped[str|None]=mapped_column(ForeignKey("users.id"))
    action: Mapped[str]=mapped_column(String(80), nullable=False)
    entity: Mapped[str]=mapped_column(String(80), nullable=False)
    entity_id: Mapped[str|None]=mapped_column(String(80))
    metadata_json: Mapped[str|None]=mapped_column(String(2000))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow, nullable=False)
