"""FastAPI HTTP layer for NTP PERMPOON Delivery Management System."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .auth import get_current_user, require_permission
from .config import settings
from .database import SessionLocal, get_db
from .models import (
    AuditLog,
    Driver,
    Job,
    JobSource,
    JobStatus,
    JobType,
    Permission,
    Role,
    User,
    Vehicle,
    VehicleStatus,
)
from .seed import seed_database


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(_: FastAPI):
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(
    title="NTP PERMPOON API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class Login(BaseModel):
    email: str
    password: str


class JobInput(BaseModel):
    source: JobSource = JobSource.EXTERNAL
    origin: str = Field(min_length=1, max_length=120)
    destination: str = Field(min_length=1, max_length=120)
    pickup_date: str = Field(min_length=1, max_length=20)
    pickup_time: str = Field(min_length=1, max_length=10)
    customer_reference: str | None = Field(default=None, max_length=160)
    notes: str | None = Field(default=None, max_length=1000)
    job_type: JobType = JobType.ONE_WAY


class AssignInput(BaseModel):
    job_id: str = Field(min_length=1, max_length=30)
    driver_id: str = Field(min_length=1, max_length=20)
    vehicle_id: str = Field(min_length=1, max_length=20)


class ProfileInput(BaseModel):
    phone: str = Field(min_length=3, max_length=30)
    address: str = Field(min_length=3, max_length=300)


class CompleteProfileInput(BaseModel):
    phone: str = Field(min_length=3, max_length=30)
    address: str = Field(min_length=3, max_length=300)
    driver_id: str = Field(min_length=1, max_length=50)
    vehicle_plate: str = Field(min_length=1, max_length=30)


class StatusInput(BaseModel):
    ready_from: str | None = Field(default=None, max_length=120)


class DestinationInput(BaseModel):
    destination: str = Field(min_length=1, max_length=120)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def audit(
    db: Session,
    actor: User | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    meta: dict | None = None,
) -> None:
    """
    Create an audit log.

    metadata_json is PostgreSQL JSONB, so pass a Python dict directly.
    Do NOT use json.dumps() here.
    """
    db.add(
        AuditLog(
            id="AUD-" + secrets.token_hex(12),
            user_id=actor.id if actor else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=meta or {},
        )
    )


def user_name(user: User) -> str:
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.email.split("@")[0]


def user_data(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user_name(user),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "address": user.address,
        "role": {
            "id": user.role.id,
            "name": user.role.name,
        },
        "permissions": [
            permission.code
            for permission in user.role.permissions
        ],
        "driver_id": user.driver.id if user.driver else None,
        "driver_business_id": (
            user.driver.driver_id
            if user.driver
            else None
        ),
        "profile_completed": user.profile_completed,
    }


def profile_data(
    user: User,
    vehicle: Vehicle | None = None,
) -> dict:
    return {
        **user_data(user),
        "position": (
            user.driver.position
            if user.driver
            else None
        ),
        "phone": user.phone,
        "address": user.address,
        "vehicle": (
            {
                "id": vehicle.id,
                "plate": vehicle.plate,
                "status": vehicle.status.value,
                "is_primary": vehicle.is_primary,
                "ready_from": vehicle.ready_from,
                "current_destination": (
                    vehicle.current_destination
                ),
            }
            if vehicle
            else None
        ),
        "last_login_at": (
            user.last_login_at.isoformat()
            if user.last_login_at
            else None
        ),
    }


def job_data(j: Job) -> dict:
    return {
        "id": j.id,
        "source": j.source.value,
        "origin": j.origin,
        "destination": j.destination,
        "pickup_date": j.pickup_date,
        "pickup_time": j.pickup_time,
        "customer_reference": j.customer_reference,
        "notes": j.notes,
        "job_type": j.job_type.value,
        "status": j.status.value,
        "driver_id": j.driver_id,
        "vehicle_id": j.vehicle_id,
        "created_by_user_id": j.created_by_user_id,
        "assigned_by_user_id": j.assigned_by_user_id,
        "assigned_at": (
            j.assigned_at.isoformat()
            if j.assigned_at
            else None
        ),
        "started_at": (
            j.started_at.isoformat()
            if j.started_at
            else None
        ),
        "completed_at": (
            j.completed_at.isoformat()
            if j.completed_at
            else None
        ),
        "created_at": (
            j.created_at.isoformat()
            if j.created_at
            else None
        ),
    }


def own_job(job: Job, user: User) -> bool:
    return bool(
        user.driver_id
        and job.driver_id == user.driver_id
    )


def get_primary_vehicle(
    db: Session,
    driver_id: str | None,
) -> Vehicle | None:
    if not driver_id:
        return None

    return db.scalar(
        select(Vehicle).where(
            Vehicle.driver_id == driver_id,
            Vehicle.is_primary.is_(True),
        )
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/v1/health")
def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@app.post("/api/v1/auth/login")
def login(payload: Login, db: DB):
    from .security import create_access_token, verify_password

    user = db.scalar(
        select(User)
        .options(
            selectinload(User.role)
            .selectinload(Role.permissions),
            selectinload(User.driver),
        )
        .where(User.email == payload.email.strip().lower())
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    if not verify_password(
        payload.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    user.last_login_at = datetime.utcnow()

    audit(
        db,
        user,
        "LOGIN",
        "USER",
        user.id,
    )

    db.commit()
    db.refresh(user)

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": user_data(user),
        "profile_completed": user.profile_completed,
    }


@app.post("/api/v1/auth/logout")
def logout(
    db: DB,
    user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    audit(
        db,
        user,
        "LOGOUT",
        "USER",
        user.id,
    )

    db.commit()

    return {"ok": True}


@app.get("/api/v1/users/me")
def me(
    user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return user_data(user)


@app.get("/api/v1/auth/me")
def auth_me(
    user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return user_data(user)


# ---------------------------------------------------------------------------
# Driver Profile
# ---------------------------------------------------------------------------

@app.post("/api/v1/profile/complete")
def complete_profile(
    payload: CompleteProfileInput,
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "profile.complete.own"
            )
        ),
    ],
):
    if user.role.name != "DRIVER":
        raise HTTPException(
            status_code=403,
            detail=(
                "Only DRIVER accounts can "
                "complete this profile"
            ),
        )

    if user.profile_completed:
        raise HTTPException(
            status_code=409,
            detail="Profile cannot be completed again",
        )

    if not user.driver:
        raise HTTPException(
            status_code=400,
            detail="Driver account has no driver record",
        )

    if user.driver.driver_id != payload.driver_id:
        raise HTTPException(
            status_code=400,
            detail="Driver ID does not match this account",
        )

    vehicle = get_primary_vehicle(
        db,
        user.driver.id,
    )

    if vehicle is None:
        vehicle = db.scalar(
            select(Vehicle)
            .where(
                Vehicle.driver_id == user.driver.id
            )
            .order_by(Vehicle.created_at.asc())
        )

    if vehicle is None:
        raise HTTPException(
            status_code=400,
            detail="Driver account has no vehicle",
        )

    duplicate_vehicle = db.scalar(
        select(Vehicle).where(
            Vehicle.plate == payload.vehicle_plate,
            Vehicle.id != vehicle.id,
        )
    )

    if duplicate_vehicle:
        raise HTTPException(
            status_code=409,
            detail="Vehicle plate is already in use",
        )

    user.phone = payload.phone
    user.address = payload.address

    vehicle.plate = payload.vehicle_plate
    vehicle.is_primary = True

    user.profile_completed = True
    user.profile_completed_at = utc_now()

    audit(
        db,
        user,
        "COMPLETE_PROFILE",
        "USER",
        user.id,
        {
            "driver_id": user.driver.id,
            "vehicle_id": vehicle.id,
        },
    )

    db.commit()

    return {
        "profile_completed": True,
        "driver_id": user.driver.id,
        "vehicle_id": vehicle.id,
        "vehicle_plate": vehicle.plate,
    }


@app.get("/api/v1/profile/me")
def profile_me(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "profile.view.own"
            )
        ),
    ],
):
    vehicle = get_primary_vehicle(
        db,
        user.driver_id,
    )

    return profile_data(
        user,
        vehicle,
    )


@app.patch("/api/v1/profile/me")
def update_own_profile(
    payload: ProfileInput,
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "profile.update.own"
            )
        ),
    ],
):
    if user.role.name != "DRIVER":
        raise HTTPException(
            status_code=403,
            detail=(
                "Only DRIVER accounts can "
                "update this profile"
            ),
        )

    if not user.profile_completed:
        raise HTTPException(
            status_code=409,
            detail="Complete your profile first",
        )

    user.phone = payload.phone
    user.address = payload.address

    audit(
        db,
        user,
        "UPDATE_PROFILE",
        "USER",
        user.id,
    )

    db.commit()

    vehicle = get_primary_vehicle(
        db,
        user.driver_id,
    )

    return profile_data(
        user,
        vehicle,
    )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.get("/api/v1/dashboard")
def dashboard(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "dashboard.view"
            )
        ),
    ],
):
    if user.role.name == "DRIVER":
        jobs = db.scalars(
            select(Job)
            .where(
                Job.driver_id == user.driver_id
            )
            .order_by(Job.created_at.desc())
        ).all()

        vehicle = get_primary_vehicle(
            db,
            user.driver_id,
        )

        return {
            "role": "DRIVER",
            "my_jobs": [
                job_data(job)
                for job in jobs
            ],
            "vehicle": (
                {
                    "id": vehicle.id,
                    "plate": vehicle.plate,
                    "status": vehicle.status.value,
                    "ready_from": vehicle.ready_from,
                    "current_destination": (
                        vehicle.current_destination
                    ),
                }
                if vehicle
                else None
            ),
        }

    vehicle_counts = {
        status.value: db.scalar(
            select(func.count())
            .select_from(Vehicle)
            .where(
                Vehicle.status == status
            )
        )
        for status in VehicleStatus
    }

    return {
        "role": user.role.name,
        "vehicle_counts": vehicle_counts,
        "created_jobs": db.scalar(
            select(func.count())
            .select_from(Job)
            .where(
                Job.status == JobStatus.CREATED
            )
        ),
        "active_jobs": db.scalar(
            select(func.count())
            .select_from(Job)
            .where(
                Job.status.in_(
                    [
                        JobStatus.ASSIGNED,
                        JobStatus.IN_PROGRESS,
                    ]
                )
            )
        ),
        "completed_jobs": db.scalar(
            select(func.count())
            .select_from(Job)
            .where(
                Job.status == JobStatus.COMPLETED
            )
        ),
    }


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

@app.get("/api/v1/jobs")
def jobs(
    db: DB,
    user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    allowed = {
        permission.code
        for permission in user.role.permissions
    }

    query = select(Job).order_by(
        Job.created_at.desc()
    )

    if "jobs.view.all" not in allowed:
        if "jobs.view.own" not in allowed:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Missing permission: "
                    "jobs.view.all"
                ),
            )

        query = query.where(
            Job.driver_id == user.driver_id
        )

    return [
        job_data(job)
        for job in db.scalars(query).all()
    ]


@app.post("/api/v1/jobs", status_code=201)
def create_job(
    payload: JobInput,
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "jobs.create"
            )
        ),
    ],
):
    job = Job(
        id=(
            f"JOB-{datetime.now():%Y%m%d}-"
            f"{secrets.token_hex(3).upper()}"
        ),
        source=payload.source,
        origin=payload.origin,
        destination=payload.destination,
        pickup_date=payload.pickup_date,
        pickup_time=payload.pickup_time,
        customer_reference=(
            payload.customer_reference
        ),
        notes=payload.notes,
        job_type=payload.job_type,
        status=JobStatus.CREATED,
        created_by_user_id=user.id,
    )

    db.add(job)

    audit(
        db,
        user,
        "CREATE",
        "JOB",
        job.id,
        {
            "job_type": job.job_type.value,
            "origin": job.origin,
            "destination": job.destination,
        },
    )

    db.commit()
    db.refresh(job)

    return job_data(job)


@app.get("/api/v1/jobs/{job_id}")
def get_job(
    job_id: str,
    db: DB,
    user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    job = db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    allowed = {
        permission.code
        for permission in user.role.permissions
    }

    if (
        "jobs.view.all" not in allowed
        and not own_job(job, user)
    ):
        raise HTTPException(
            status_code=403,
            detail="Not your job",
        )

    return job_data(job)


@app.post("/api/v1/jobs/{job_id}/cancel")
def cancel_job(
    job_id: str,
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "jobs.cancel"
            )
        ),
    ],
):
    job = db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    if job.status in [
        JobStatus.COMPLETED,
        JobStatus.CANCELLED,
    ]:
        raise HTTPException(
            status_code=409,
            detail="Job cannot be cancelled",
        )

    if job.vehicle_id:
        vehicle = db.get(
            Vehicle,
            job.vehicle_id,
        )

        if vehicle:
            vehicle.status = VehicleStatus.AVAILABLE
            vehicle.ready_from = job.origin
            vehicle.current_destination = None

    job.status = JobStatus.CANCELLED

    audit(
        db,
        user,
        "CANCEL",
        "JOB",
        job.id,
    )

    db.commit()

    return job_data(job)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

@app.get("/api/v1/dispatch/candidates")
def candidates(
    db: DB,
    origin: str = Query(
        default="",
        max_length=120,
    ),
    driver_name: str = Query(
        default="",
        max_length=120,
    ),
    vehicle_plate: str = Query(
        default="",
        max_length=30,
    ),
    user: Annotated[
        User,
        Depends(
            require_permission(
                "dispatch.view"
            )
        ),
    ] = None,
):
    query = (
        select(Vehicle)
        .options(
            selectinload(Vehicle.driver)
            .selectinload(Driver.user),
        )
        .where(
            Vehicle.status.in_(
                [
                    VehicleStatus.AVAILABLE,
                    VehicleStatus.AVAILABLE_RETURN,
                ]
            )
        )
    )

    rows = []

    for vehicle in db.scalars(query).all():
        driver = vehicle.driver
        driver_user = (
            driver.user
            if driver
            else None
        )

        if not driver:
            continue

        if not driver.is_active:
            continue

        if origin:
            available_here = (
                vehicle.status
                == VehicleStatus.AVAILABLE
                and vehicle.ready_from == origin
            )

            return_here = (
                vehicle.status
                == VehicleStatus.AVAILABLE_RETURN
                and vehicle.current_destination
                == origin
            )

            if not (
                available_here
                or return_here
            ):
                continue

        display_name = (
            user_name(driver_user)
            if driver_user
            else driver.driver_id
        )

        if (
            driver_name
            and driver_name.lower()
            not in display_name.lower()
        ):
            continue

        if (
            vehicle_plate
            and vehicle_plate.lower()
            not in vehicle.plate.lower()
        ):
            continue

        rows.append(
            {
                "vehicle_id": vehicle.id,
                "vehicle_plate": vehicle.plate,
                "driver_id": driver.id,
                "driver_business_id": (
                    driver.driver_id
                ),
                "driver_name": display_name,
                "operational_status": (
                    vehicle.status.value
                ),
                "ready_from": vehicle.ready_from,
                "current_destination": (
                    vehicle.current_destination
                ),
                "candidate_type": (
                    "return"
                    if vehicle.status
                    == VehicleStatus.AVAILABLE_RETURN
                    else "available"
                ),
            }
        )

    return {
        "items": rows,
        "total": len(rows),
    }


@app.post("/api/v1/dispatch/assign")
def assign(
    payload: AssignInput,
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "dispatch.assign"
            )
        ),
    ],
):
    """
    Assign a driver + vehicle to a CREATED job.

    Vehicle and job rows are locked during the transaction
    so that two administrators cannot successfully assign
    the same vehicle at once.
    """

    try:
        with db.begin_nested():
            job = db.scalar(
                select(Job)
                .where(
                    Job.id == payload.job_id
                )
                .with_for_update()
            )

            vehicle = db.scalar(
                select(Vehicle)
                .where(
                    Vehicle.id == payload.vehicle_id
                )
                .with_for_update()
            )

            driver = db.scalar(
                select(Driver)
                .where(
                    Driver.id == payload.driver_id
                )
            )

            if (
                not job
                or not vehicle
                or not driver
            ):
                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Job, driver, or "
                        "vehicle not found"
                    ),
                )

            if job.status != JobStatus.CREATED:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Job is not available "
                        "for assignment"
                    ),
                )

            if not driver.is_active:
                raise HTTPException(
                    status_code=409,
                    detail="Driver is not active",
                )

            if vehicle.driver_id != driver.id:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Vehicle does not belong "
                        "to this driver"
                    ),
                )

            if vehicle.status not in [
                VehicleStatus.AVAILABLE,
                VehicleStatus.AVAILABLE_RETURN,
            ]:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Vehicle is no longer "
                        "available"
                    ),
                )

            job.driver_id = driver.id
            job.vehicle_id = vehicle.id
            job.assigned_by_user_id = user.id
            job.assigned_at = utc_now()
            job.status = JobStatus.ASSIGNED

            vehicle.status = VehicleStatus.BUSY
            vehicle.ready_from = None

            audit(
                db,
                user,
                "ASSIGN",
                "JOB",
                job.id,
                {
                    "vehicle_id": vehicle.id,
                    "driver_id": driver.id,
                    "assigned_by_user_id": user.id,
                },
            )

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    return job_data(job)


# ---------------------------------------------------------------------------
# Driver's own jobs / availability
# ---------------------------------------------------------------------------

@app.get("/api/v1/my/jobs")
def my_jobs(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "jobs.view.own"
            )
        ),
    ],
):
    jobs = db.scalars(
        select(Job)
        .where(
            Job.driver_id == user.driver_id
        )
        .order_by(Job.created_at.desc())
    ).all()

    return [
        job_data(job)
        for job in jobs
    ]


@app.post("/api/v1/my/check-in")
def check_in(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "availability.check_in"
            )
        ),
    ],
):
    if not user.driver:
        raise HTTPException(
            status_code=400,
            detail="Driver profile not found",
        )

    audit(
        db,
        user,
        "CHECK_IN",
        "DRIVER",
        user.driver.id,
    )

    db.commit()

    return {
        "ok": True,
        "driver_id": user.driver.id,
    }


@app.post("/api/v1/my/ready")
def ready(
    payload: StatusInput,
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "availability.update.own"
            )
        ),
    ],
):
    vehicle = get_primary_vehicle(
        db,
        user.driver_id,
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Primary vehicle not found",
        )

    if vehicle.status in [
        VehicleStatus.MAINTENANCE,
        VehicleStatus.BUSY,
    ]:
        raise HTTPException(
            status_code=409,
            detail="Vehicle cannot be set ready",
        )

    if not payload.ready_from:
        raise HTTPException(
            status_code=422,
            detail=(
                "ready_from is required when "
                "setting vehicle ready"
            ),
        )

    vehicle.status = VehicleStatus.AVAILABLE
    vehicle.ready_from = payload.ready_from
    vehicle.current_destination = None

    audit(
        db,
        user,
        "READY",
        "VEHICLE",
        vehicle.id,
        {
            "ready_from": vehicle.ready_from,
        },
    )

    db.commit()

    return {
        "status": vehicle.status.value,
        "vehicle_id": vehicle.id,
        "ready_from": vehicle.ready_from,
    }


@app.post("/api/v1/my/not-ready")
def not_ready(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "availability.update.own"
            )
        ),
    ],
):
    vehicle = get_primary_vehicle(
        db,
        user.driver_id,
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Primary vehicle not found",
        )

    if vehicle.status == VehicleStatus.BUSY:
        raise HTTPException(
            status_code=409,
            detail=(
                "Busy vehicle cannot be "
                "set not ready"
            ),
        )

    vehicle.status = VehicleStatus.NOT_READY
    vehicle.ready_from = None
    vehicle.current_destination = None

    audit(
        db,
        user,
        "NOT_READY",
        "VEHICLE",
        vehicle.id,
    )

    db.commit()

    return {
        "status": vehicle.status.value,
        "vehicle_id": vehicle.id,
    }


# ---------------------------------------------------------------------------
# Driver job operations
# ---------------------------------------------------------------------------

@app.post("/api/v1/my/jobs/{job_id}/start")
def start(
    job_id: str,
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "jobs.start.own"
            )
        ),
    ],
):
    job = db.get(Job, job_id)

    if not job or not own_job(job, user):
        raise HTTPException(
            status_code=404,
            detail="Assigned job not found",
        )

    if job.status != JobStatus.ASSIGNED:
        raise HTTPException(
            status_code=409,
            detail="Job cannot be started",
        )

    job.status = JobStatus.IN_PROGRESS
    job.started_at = utc_now()

    audit(
        db,
        user,
        "START",
        "JOB",
        job.id,
    )

    db.commit()

    return job_data(job)


@app.patch("/api/v1/my/jobs/{job_id}/destination")
def change_destination(
    job_id: str,
    payload: DestinationInput,
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "jobs.change_destination.own"
            )
        ),
    ],
):
    job = db.get(Job, job_id)

    if (
        not job
        or not own_job(job, user)
        or job.status != JobStatus.IN_PROGRESS
    ):
        raise HTTPException(
            status_code=409,
            detail="Active assigned job required",
        )

    old_destination = job.destination
    job.destination = payload.destination

    audit(
        db,
        user,
        "CHANGE_DESTINATION",
        "JOB",
        job.id,
        {
            "old_destination": old_destination,
            "new_destination": job.destination,
        },
    )

    db.commit()

    return job_data(job)


@app.post("/api/v1/my/jobs/{job_id}/close")
def close(
    job_id: str,
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "jobs.close.own"
            )
        ),
    ],
):
    job = db.get(Job, job_id)

    if (
        not job
        or not own_job(job, user)
        or job.status != JobStatus.IN_PROGRESS
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "In-progress assigned "
                "job required"
            ),
        )

    vehicle = (
        db.get(Vehicle, job.vehicle_id)
        if job.vehicle_id
        else None
    )

    if not vehicle:
        raise HTTPException(
            status_code=409,
            detail="Assigned vehicle not found",
        )

    job.status = JobStatus.COMPLETED
    job.completed_at = utc_now()

    if job.job_type == JobType.ONE_WAY:
        vehicle.status = (
            VehicleStatus.AVAILABLE_RETURN
        )
        vehicle.current_destination = (
            job.destination
        )
        vehicle.ready_from = None

    else:
        vehicle.status = VehicleStatus.AVAILABLE
        vehicle.current_destination = None
        vehicle.ready_from = job.destination

    audit(
        db,
        user,
        "CLOSE",
        "JOB",
        job.id,
        {
            "vehicle_id": vehicle.id,
            "vehicle_status": vehicle.status.value,
        },
    )

    db.commit()

    return job_data(job)


# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------

@app.get("/api/v1/drivers")
def drivers(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "drivers.view.all"
            )
        ),
    ],
):
    rows = db.scalars(
        select(Driver)
        .options(
            selectinload(Driver.user),
            selectinload(Driver.vehicles),
        )
        .order_by(Driver.driver_id)
    ).all()

    result = []

    for driver in rows:
        driver_user = driver.user

        primary_vehicle = next(
            (
                vehicle
                for vehicle in driver.vehicles
                if vehicle.is_primary
            ),
            None,
        )

        result.append(
            {
                "id": driver.id,
                "driver_id": driver.driver_id,
                "first_name": (
                    driver_user.first_name
                    if driver_user
                    else None
                ),
                "last_name": (
                    driver_user.last_name
                    if driver_user
                    else None
                ),
                "name": (
                    user_name(driver_user)
                    if driver_user
                    else driver.driver_id
                ),
                "email": (
                    driver_user.email
                    if driver_user
                    else None
                ),
                "phone": (
                    driver_user.phone
                    if driver_user
                    else None
                ),
                "address": (
                    driver_user.address
                    if driver_user
                    else None
                ),
                "position": driver.position,
                "is_active": driver.is_active,
                "profile_completed": (
                    driver_user.profile_completed
                    if driver_user
                    else False
                ),
                "primary_vehicle": (
                    {
                        "id": primary_vehicle.id,
                        "plate": primary_vehicle.plate,
                        "status": (
                            primary_vehicle.status.value
                        ),
                    }
                    if primary_vehicle
                    else None
                ),
            }
        )

    return result


# Backward-compatible alias for existing frontend code.
@app.get("/api/v1/employees")
def employees_alias(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "drivers.view.all"
            )
        ),
    ],
):
    rows = db.scalars(
        select(Driver)
        .options(
            selectinload(Driver.user)
        )
        .order_by(Driver.driver_id)
    ).all()

    return [
        {
            "id": driver.id,
            "driver_id": driver.driver_id,
            "name": (
                user_name(driver.user)
                if driver.user
                else driver.driver_id
            ),
            "position": driver.position,
            "phone": (
                driver.user.phone
                if driver.user
                else None
            ),
            "is_active": driver.is_active,
        }
        for driver in rows
    ]


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------

@app.get("/api/v1/vehicles")
def vehicles(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "vehicles.view.all"
            )
        ),
    ],
):
    rows = db.scalars(
        select(Vehicle)
        .options(
            selectinload(Vehicle.driver)
            .selectinload(Driver.user),
        )
        .order_by(Vehicle.plate)
    ).all()

    return [
        {
            "id": vehicle.id,
            "plate": vehicle.plate,
            "driver_id": vehicle.driver_id,
            "driver_business_id": (
                vehicle.driver.driver_id
                if vehicle.driver
                else None
            ),
            "driver_name": (
                user_name(vehicle.driver.user)
                if (
                    vehicle.driver
                    and vehicle.driver.user
                )
                else None
            ),
            "status": vehicle.status.value,
            "is_primary": vehicle.is_primary,
            "ready_from": vehicle.ready_from,
            "current_destination": (
                vehicle.current_destination
            ),
        }
        for vehicle in rows
    ]


# ---------------------------------------------------------------------------
# Roles / Permissions
# ---------------------------------------------------------------------------

@app.get("/api/v1/roles")
def roles(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "roles.view"
            )
        ),
    ],
):
    rows = db.scalars(
        select(Role)
        .options(
            selectinload(Role.permissions),
            selectinload(Role.users),
        )
        .order_by(Role.name)
    ).all()

    return [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_system_role": role.is_system_role,
            "users_count": len(role.users),
            "permissions": [
                permission.code
                for permission in role.permissions
            ],
        }
        for role in rows
    ]


@app.get("/api/v1/permissions")
def permissions(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "permissions.view"
            )
        ),
    ],
):
    rows = db.scalars(
        select(Permission).order_by(
            Permission.module,
            Permission.action,
            Permission.code,
        )
    ).all()

    return [
        {
            "id": permission.id,
            "code": permission.code,
            "module": permission.module,
            "action": permission.action,
            "scope": permission.scope,
            "description": permission.description,
        }
        for permission in rows
    ]


# ---------------------------------------------------------------------------
# Audit logs
# ---------------------------------------------------------------------------

@app.get("/api/v1/audit-logs")
def logs(
    db: DB,
    user: Annotated[
        User,
        Depends(
            require_permission(
                "audit_logs.view"
            )
        ),
    ],
):
    rows = db.scalars(
        select(AuditLog)
        .options(
            selectinload(AuditLog.user)
        )
        .order_by(
            AuditLog.created_at.desc()
        )
        .limit(100)
    ).all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_name": (
                user_name(log.user)
                if log.user
                else None
            ),
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,

            # metadata_json is JSONB, so SQLAlchemy
            # already returns a Python dict.
            "metadata": log.metadata_json or {},

            "created_at": (
                log.created_at.isoformat()
                if log.created_at
                else None
            ),
        }
        for log in rows
    ]