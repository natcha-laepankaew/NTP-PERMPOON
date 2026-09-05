from contextlib import asynccontextmanager
from datetime import datetime, timezone
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .auth import get_current_user, require_permission
from .database import SessionLocal, get_db
from .models import Employee, Job, JobSource, JobStatus, JobType, User, Vehicle, VehicleStatus
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    with SessionLocal() as session:
        seed_database(session)
    yield


app = FastAPI(title="NTP PERMPOON API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DbSession = Annotated[Session, Depends(get_db)]


class CreateJobRequest(BaseModel):
    source: JobSource = JobSource.EXTERNAL
    origin: str = Field(min_length=1, max_length=120)
    destination: str = Field(min_length=1, max_length=120)
    pickup_date: str = Field(min_length=1, max_length=20)
    pickup_time: str = Field(min_length=1, max_length=10)
    customer_reference: str | None = Field(default=None, max_length=160)
    notes: str | None = Field(default=None, max_length=1000)
    job_type: JobType = JobType.ONE_WAY


class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ntp-permpoon-api"}


@app.post("/api/v1/auth/login", responses={401: {"description": "Invalid credentials"}})
def login(payload: LoginRequest, db: DbSession) -> dict:
    from .security import create_access_token, verify_password

    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "profile_completed": user.profile_completed, "roles": [role.name for role in user.roles]}


@app.get("/api/v1/auth/me")
def me(current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    return {"id": current_user.id, "email": current_user.email, "roles": [role.name for role in current_user.roles], "profile_completed": current_user.profile_completed}


@app.post("/api/v1/jobs", status_code=201)
def create_job(payload: CreateJobRequest, db: DbSession, _: Annotated[User, Depends(require_permission("jobs.create"))]) -> dict:
    job_id = f"JOB-{datetime.now(timezone.utc):%Y%m%d}-{secrets.token_hex(3).upper()}"
    job = Job(id=job_id, **payload.model_dump(), status=JobStatus.CREATED)
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"id": job.id, "status": job.status.value, "origin": job.origin, "destination": job.destination}


@app.get("/api/v1/dashboard/manager")
def manager_dashboard(db: DbSession, _: Annotated[User, Depends(require_permission("dashboard.view"))]) -> dict:
    vehicles = db.scalars(select(Vehicle)).all()
    counts = {status.value: 0 for status in VehicleStatus}
    for vehicle in vehicles:
        counts[vehicle.status.value] += 1
    return {
        "counts": counts,
        "today_jobs": 42,
        "active_jobs": 15,
        "completed_jobs": 27,
    }


@app.get("/api/v1/dispatch/candidates")
def dispatch_candidates(
    db: DbSession,
    origin: Annotated[str, Query()] = "",
    employee_name: Annotated[str, Query()] = "",
    vehicle_plate: Annotated[str, Query()] = "",
    status: Annotated[VehicleStatus | None, Query()] = None,
    _: Annotated[User, Depends(require_permission("dispatch.view"))] = None,
) -> dict:
    query = select(Vehicle, Employee).join(Employee, Vehicle.employee_id == Employee.id, isouter=True)
    if status:
        query = query.where(Vehicle.status == status)
    if origin:
        query = query.where((Vehicle.ready_from == origin) | (Vehicle.current_destination == origin))
    if employee_name:
        query = query.where(Employee.name.ilike(f"%{employee_name}%"))
    if vehicle_plate:
        query = query.where(Vehicle.plate.ilike(f"%{vehicle_plate}%"))

    results = [candidate_response(vehicle, employee) for vehicle, employee in db.execute(query).all() if is_candidate(vehicle, origin)]
    return {"items": results, "total": len(results)}


def is_candidate(vehicle: Vehicle, origin: str) -> bool:
    if not origin:
        return True
    if vehicle.status == VehicleStatus.AVAILABLE:
        return vehicle.ready_from == origin
    if vehicle.status == VehicleStatus.AVAILABLE_RETURN:
        return vehicle.current_destination == origin
    return False


def apply_candidate_filters(query, status: VehicleStatus | None, origin: str, employee_name: str, vehicle_plate: str):
    filters = []
    if status:
        filters.append(Vehicle.status == status)
    if origin:
        filters.append((Vehicle.ready_from == origin) | (Vehicle.current_destination == origin))
    if employee_name:
        filters.append(Employee.name.ilike(f"%{employee_name}%"))
    if vehicle_plate:
        filters.append(Vehicle.plate.ilike(f"%{vehicle_plate}%"))
    return query.where(*filters)


def candidate_response(vehicle: Vehicle, employee: Employee | None) -> dict:
    return {
        "vehicle_id": vehicle.id,
        "vehicle_plate": vehicle.plate,
        "employee_id": employee.id if employee else None,
        "employee_name": employee.name if employee else "ยังไม่มอบหมาย",
        "operational_status": vehicle.status.value,
        "ready_from": vehicle.ready_from,
        "current_destination": vehicle.current_destination,
        "candidate_type": "return" if vehicle.status == VehicleStatus.AVAILABLE_RETURN else "available",
    }


@app.get("/api/v1/employees")
def employees(db: DbSession, _: Annotated[User, Depends(require_permission("employees.view.all"))]) -> list[dict]:
    rows = db.execute(select(Employee, Vehicle).join(Vehicle, Vehicle.employee_id == Employee.id, isouter=True)).all()
    return [
        {
            "id": employee.id,
            "name": employee.name,
            "position": employee.position,
            "phone": employee.phone,
            "vehicle_plate": vehicle.plate if vehicle else None,
            "status": vehicle.status.value if vehicle else "NOT_READY",
        }
        for employee, vehicle in rows
    ]
