# app/models.py

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Table,
    Column,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.dialects.postgresql import JSONB

# =========================================================
# Base
# =========================================================

class Base(DeclarativeBase):
    pass


# =========================================================
# Common Timestamp
# =========================================================

class Timestamped:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# =========================================================
# Enums
# =========================================================

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


# =========================================================
# Role / Permission
# =========================================================

role_permissions = Table(
    "role_permissions",
    Base.metadata,

    Column(
        "role_id",
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),

    Column(
        "permission_id",
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base, Timestamped):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(240),
        nullable=False,
    )

    is_system_role: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    users: Mapped[list["User"]] = relationship(
        back_populates="role",
    )

    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(
        String(80),
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )

    module: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    scope: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        String(240),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions,
        back_populates="permissions",
    )


# =========================================================
# Driver
# =========================================================

class Driver(Base, Timestamped):
    """
    ข้อมูลเฉพาะของ Driver

    Account / Login:
        User

    Driver-specific:
        Driver.driver_id
        Driver.position
        Driver.is_active
    """

    __tablename__ = "drivers"

    id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    driver_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    position: Mapped[str] = mapped_column(
        String(50),
        default="DRIVER",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    user: Mapped["User | None"] = relationship(
        back_populates="driver",
        uselist=False,
    )

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="driver",
    )

    jobs: Mapped[list["Job"]] = relationship(
        back_populates="driver",
        foreign_keys="Job.driver_id",
    )


# =========================================================
# User
# =========================================================

class User(Base, Timestamped):
    """
    Account หลักของระบบ

    Role:
        ADMINISTRATOR
        ADMIN
        MANAGER
        DRIVER

    Login:
        email + password

    DRIVER:
        driver_id จะเชื่อมผ่าน driver_id
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    email: Mapped[str] = mapped_column(
        String(160),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # -----------------------------------------------------
    # Role
    # -----------------------------------------------------

    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
        index=True,
    )

    # -----------------------------------------------------
    # Driver relation
    #
    # NULL:
    #   ADMINISTRATOR
    #   ADMIN
    #   MANAGER
    #
    # มีค่า:
    #   DRIVER
    # -----------------------------------------------------

    driver_id: Mapped[str | None] = mapped_column(
        ForeignKey("drivers.id"),
        unique=True,
        nullable=True,
        index=True,
    )

    # -----------------------------------------------------
    # Profile
    # -----------------------------------------------------

    first_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    # -----------------------------------------------------
    # Account status
    # -----------------------------------------------------

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -----------------------------------------------------
    # Profile completion
    # -----------------------------------------------------

    profile_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    profile_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # -----------------------------------------------------
    # Login tracking
    # -----------------------------------------------------

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    role: Mapped["Role"] = relationship(
        back_populates="users",
    )

    driver: Mapped["Driver | None"] = relationship(
        back_populates="user",
        uselist=False,
    )

    # Jobs created by this user
    created_jobs: Mapped[list["Job"]] = relationship(
        back_populates="created_by",
        foreign_keys="Job.created_by_user_id",
    )

    # Jobs assigned by this user
    assigned_jobs: Mapped[list["Job"]] = relationship(
        back_populates="assigned_by",
        foreign_keys="Job.assigned_by_user_id",
    )

    # Audit logs generated by this user
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
        foreign_keys="AuditLog.user_id",
    )


# =========================================================
# Vehicle
# =========================================================

class Vehicle(Base, Timestamped):
    """
    รถของ Driver

    Driver 1 คน
        |
        +---- Vehicle 1
        +---- Vehicle 2
        +---- Vehicle 3

    และกำหนดรถหลักได้เพียง 1 คัน
    """

    __tablename__ = "vehicles"

    __table_args__ = (
        Index(
            "uq_one_primary_vehicle_per_driver",
            "driver_id",
            unique=True,
            postgresql_where=Column("is_primary") == True,
        ),
    )

    id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    plate: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    driver_id: Mapped[str] = mapped_column(
        ForeignKey(
            "drivers.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    status: Mapped[VehicleStatus] = mapped_column(
        default=VehicleStatus.NOT_READY,
        nullable=False,
    )

    # จุดที่รถพร้อมรับงาน
    ready_from: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    # ปลายทางปัจจุบันของรถ
    current_destination: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    driver: Mapped["Driver"] = relationship(
        back_populates="vehicles",
    )

    jobs: Mapped[list["Job"]] = relationship(
        back_populates="vehicle",
    )


# =========================================================
# Job
# =========================================================

class Job(Base, Timestamped):
    """
    งานขนส่ง

    ผู้สร้างงาน:
        created_by_user_id

    ผู้มอบหมายงาน:
        assigned_by_user_id

    Driver:
        driver_id

    Vehicle:
        vehicle_id
    """

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    # -----------------------------------------------------
    # Job source
    # -----------------------------------------------------

    source: Mapped[JobSource] = mapped_column(
        default=JobSource.EXTERNAL,
        nullable=False,
    )

    # -----------------------------------------------------
    # Route
    # -----------------------------------------------------

    origin: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    destination: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    # -----------------------------------------------------
    # Schedule
    # -----------------------------------------------------

    pickup_date: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    pickup_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # -----------------------------------------------------
    # Customer / Note
    # -----------------------------------------------------

    customer_reference: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # -----------------------------------------------------
    # Job type
    # -----------------------------------------------------

    job_type: Mapped[JobType] = mapped_column(
        default=JobType.ONE_WAY,
        nullable=False,
    )

    # -----------------------------------------------------
    # Job status
    # -----------------------------------------------------

    status: Mapped[JobStatus] = mapped_column(
        default=JobStatus.CREATED,
        nullable=False,
        index=True,
    )

    # -----------------------------------------------------
    # Driver
    # -----------------------------------------------------

    driver_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "drivers.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # -----------------------------------------------------
    # Vehicle
    # -----------------------------------------------------

    vehicle_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "vehicles.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # -----------------------------------------------------
    # Created by
    # -----------------------------------------------------

    created_by_user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # -----------------------------------------------------
    # Assigned by
    # -----------------------------------------------------

    assigned_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # -----------------------------------------------------
    # Timestamps
    # -----------------------------------------------------

    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    driver: Mapped["Driver | None"] = relationship(
        back_populates="jobs",
        foreign_keys=[driver_id],
    )

    vehicle: Mapped["Vehicle | None"] = relationship(
        back_populates="jobs",
    )

    created_by: Mapped["User"] = relationship(
        back_populates="created_jobs",
        foreign_keys=[created_by_user_id],
    )

    assigned_by: Mapped["User | None"] = relationship(
        back_populates="assigned_jobs",
        foreign_keys=[assigned_by_user_id],
    )

    evidences: Mapped[list["JobEvidence"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


# =========================================================
# Job Evidence
# =========================================================

class JobEvidence(Base):
    """
    หลักฐานปิดงาน

    เช่น:
        JPG
        PNG
        PDF
    """

    __tablename__ = "job_evidences"

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    job_id: Mapped[str] = mapped_column(
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    file_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # -----------------------------------------------------
    # Relationship
    # -----------------------------------------------------

    job: Mapped["Job"] = relationship(
        back_populates="evidences",
    )


# =========================================================
# Audit Log
# =========================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)

    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entity_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    user: Mapped["User | None"] = relationship(
        back_populates="audit_logs"
    )