from contextlib import asynccontextmanager
from datetime import datetime, timezone
import secrets
import json
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .auth import get_current_user, require_permission
from .database import SessionLocal, get_db
from .models import AuditLog, Employee, Job, JobSource, JobStatus, JobType, Permission, Role, User, Vehicle, VehicleStatus
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


class CompleteProfileRequest(BaseModel):
    phone: str = Field(min_length=3, max_length=30)
    address: str = Field(min_length=3, max_length=300)


class CreateEmployeeRequest(BaseModel):
    employee_id: str = Field(min_length=2, max_length=20)
    name: str = Field(min_length=2, max_length=120)
    position: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=5, max_length=160)
    phone: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=128)


def write_audit(db: Session, actor: User | None, action: str, entity: str, entity_id: str | None = None, metadata: dict | None = None) -> None:
    db.add(AuditLog(id=f"AUD-{secrets.token_hex(12)}", actor_user_id=actor.id if actor else None, action=action, entity=entity, entity_id=entity_id, metadata_json=json.dumps(metadata or {}, ensure_ascii=False)))


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ntp-permpoon-api"}


@app.post("/api/v1/auth/login", responses={401: {"description": "Invalid credentials"}})
def login(payload: LoginRequest, db: DbSession) -> dict:
    from .security import create_access_token, verify_password

    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    write_audit(db, user, "LOGIN", "USER", user.id)
    db.commit()
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "profile_completed": user.profile_completed, "roles": [role.name for role in user.roles]}


@app.get("/api/v1/auth/me")
def me(current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    return {"id": current_user.id, "email": current_user.email, "roles": [role.name for role in current_user.roles], "profile_completed": current_user.profile_completed}


@app.post("/api/v1/profile/complete", responses={400: {"description": "Employee profile is not linked"}, 409: {"description": "Profile is already completed"}})
def complete_profile(payload: CompleteProfileRequest, db: DbSession, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    if current_user.profile_completed:
        raise HTTPException(status_code=409, detail="Profile is already completed")
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="Employee profile is not linked")
    current_user.employee.phone = payload.phone
    current_user.employee.address = payload.address
    current_user.profile_completed = True
    current_user.profile_completed_at = datetime.now(timezone.utc)
    write_audit(db, current_user, "COMPLETE_PROFILE", "USER", current_user.id)
    db.commit()
    return {"profile_completed": True}


@app.get("/api/v1/roles")
def list_roles(db: DbSession, _: Annotated[User, Depends(require_permission("roles.view"))]) -> list[dict]:
    roles = db.scalars(select(Role)).all()
    return [{"id": role.id, "name": role.name, "description": role.description, "is_system_role": role.is_system_role, "users_count": len(role.users), "permissions": sorted(permission.code for permission in role.permissions)} for role in roles]


@app.get("/api/v1/permissions")
def list_permissions(db: DbSession, _: Annotated[User, Depends(require_permission("permissions.view"))]) -> list[dict]:
    return [{"code": item.code, "module": item.module, "action": item.action, "scope": item.scope, "description": item.description} for item in db.scalars(select(Permission).order_by(Permission.module, Permission.code)).all()]


@app.get("/api/v1/audit-logs")
def list_audit_logs(db: DbSession, _: Annotated[User, Depends(require_permission("audit_logs.view"))]) -> list[dict]:
    logs = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)).all()
    return [{"id": log.id, "actor_user_id": log.actor_user_id, "action": log.action, "entity": log.entity, "entity_id": log.entity_id, "metadata": log.metadata_json, "created_at": log.created_at.isoformat()} for log in logs]


@app.post("/api/v1/employees", status_code=201, responses={409: {"description": "Employee ID or email already exists"}, 500: {"description": "EMPLOYEE role is not configured"}})
def create_employee(payload: CreateEmployeeRequest, db: DbSession, actor: Annotated[User, Depends(require_permission("employees.create"))]) -> dict:
    if db.scalar(select(Employee).where(Employee.id == payload.employee_id)) or db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail="Employee ID or email already exists")
    from .security import hash_password
    employee = Employee(id=payload.employee_id, name=payload.name, position=payload.position, phone=payload.phone)
    user = User(id=f"U-{secrets.token_hex(6).upper()}", email=payload.email.lower(), password_hash=hash_password(payload.password), employee_id=payload.employee_id, profile_completed=False)
    employee_user_role = db.scalar(select(Role).where(Role.name == "EMPLOYEE"))
    if not employee_user_role:
        raise HTTPException(status_code=500, detail="EMPLOYEE role is not configured")
    user.roles = [employee_user_role]
    db.add_all([employee, user])
    write_audit(db, actor, "CREATE_EMPLOYEE", "EMPLOYEE", employee.id, {"email": user.email, "position": employee.position})
    db.commit()
    return {"id": employee.id, "email": user.email, "profile_completed": False}


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


@app.get("/api/v1/jobs")
def list_jobs(db: DbSession, _: Annotated[User, Depends(require_permission("jobs.view.all"))]) -> list[dict]:
    return [{"id": job.id, "origin": job.origin, "destination": job.destination, "source": job.source.value, "job_type": job.job_type.value, "status": job.status.value, "pickup_date": job.pickup_date, "pickup_time": job.pickup_time} for job in db.scalars(select(Job).order_by(Job.created_at.desc())).all()]


@app.get("/api/v1/vehicles")
def list_vehicles(db: DbSession, _: Annotated[User, Depends(require_permission("vehicles.view.all"))]) -> list[dict]:
    rows = db.execute(select(Vehicle, Employee).join(Employee, Vehicle.employee_id == Employee.id, isouter=True)).all()
    return [{"id": vehicle.id, "plate": vehicle.plate, "employee": employee.name if employee else None, "status": vehicle.status.value, "ready_from": vehicle.ready_from, "current_destination": vehicle.current_destination} for vehicle, employee in rows]


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
