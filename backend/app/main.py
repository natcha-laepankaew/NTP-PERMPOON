"""HTTP layer. State transitions and permission checks stay server-side."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json, secrets
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from .auth import get_current_user, require_permission
from .config import settings
from .database import SessionLocal, get_db
from .models import AuditLog, Employee, Job, JobSource, JobStatus, JobType, Permission, Role, User, Vehicle, VehicleStatus
from .seed import seed_database

@asynccontextmanager
async def lifespan(_: FastAPI):
    with SessionLocal() as db: seed_database(db)
    yield
app=FastAPI(title="NTP PERMPOON API",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origin_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
DB=Annotated[Session,Depends(get_db)]

class Login(BaseModel): email:str; password:str
class JobInput(BaseModel):
    source:JobSource=JobSource.EXTERNAL; origin:str=Field(min_length=1,max_length=120); destination:str=Field(min_length=1,max_length=120); pickup_date:str; pickup_time:str; customer_reference:str|None=None; notes:str|None=None; job_type:JobType=JobType.ONE_WAY
class AssignInput(BaseModel): job_id:str; employee_id:str; vehicle_id:str
class ProfileInput(BaseModel): phone:str=Field(min_length=3); address:str=Field(min_length=3)
class StatusInput(BaseModel): ready_from:str|None=None
class DestinationInput(BaseModel): destination:str=Field(min_length=1,max_length=120)

def audit(db,actor,action,entity,entity_id=None,meta=None): db.add(AuditLog(id="AUD-"+secrets.token_hex(12),actor_user_id=actor.id if actor else None,action=action,entity=entity,entity_id=entity_id,metadata_json=json.dumps(meta or {})))
def user_data(user): return {"id":user.id,"email":user.email,"name":user.employee.name if user.employee else user.email.split("@")[0],"role":{"id":user.role.id,"name":user.role.name},"permissions":[p.code for p in user.role.permissions],"profile_completed":user.profile_completed}
def job_data(j): return {"id":j.id,"source":j.source.value,"origin":j.origin,"destination":j.destination,"pickup_date":j.pickup_date,"pickup_time":j.pickup_time,"job_type":j.job_type.value,"status":j.status.value,"driver_id":j.driver_id,"vehicle_id":j.vehicle_id}
def own_job(job,user): return bool(user.employee_id and job.driver_id==user.employee_id)

@app.get("/api/v1/health")
def health(): return {"status":"ok"}
@app.post("/api/v1/auth/login")
def login(payload:Login,db:DB):
    from .security import create_access_token,verify_password
    user=db.scalar(select(User).options(selectinload(User.role).selectinload(Role.permissions),selectinload(User.employee)).where(User.email==payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password,user.password_hash): raise HTTPException(401,"Invalid email or password")
    user.last_login_at=datetime.now(timezone.utc); audit(db,user,"LOGIN","USER",user.id); db.commit()
    return {"access_token":create_access_token(user.id),"token_type":"bearer","user":user_data(user),"profile_completed":user.profile_completed}
@app.post("/api/v1/auth/logout")
def logout(db:DB,user:Annotated[User,Depends(get_current_user)]): audit(db,user,"LOGOUT","USER",user.id);db.commit();return {"ok":True}
@app.get("/api/v1/users/me")
def me(user:Annotated[User,Depends(get_current_user)]): return user_data(user)
@app.get("/api/v1/auth/me")
def auth_me(user:Annotated[User,Depends(get_current_user)]): return user_data(user)

@app.post("/api/v1/profile/complete")
def complete_profile(payload:ProfileInput,db:DB,user:Annotated[User,Depends(require_permission("profile.complete.own"))]):
    if user.role.name!="DRIVER" or user.profile_completed: raise HTTPException(409,"Profile cannot be completed again")
    if not user.employee: raise HTTPException(400,"Driver account has no employee")
    user.employee.phone=payload.phone; user.employee.address=payload.address; user.profile_completed=True; user.profile_completed_at=datetime.now(timezone.utc); audit(db,user,"COMPLETE_PROFILE","USER",user.id);db.commit();return {"profile_completed":True}

@app.get("/api/v1/dashboard")
def dashboard(db:DB,user:Annotated[User,Depends(require_permission("dashboard.view"))]):
    if user.role.name=="DRIVER":
        jobs=db.scalars(select(Job).where(Job.driver_id==user.employee_id)).all(); vehicle=db.scalar(select(Vehicle).where(Vehicle.employee_id==user.employee_id,Vehicle.is_primary==True)); return {"role":"DRIVER","my_jobs":[job_data(x) for x in jobs],"vehicle":vehicle.status.value if vehicle else None}
    counts={s.value:db.scalar(select(func.count()).select_from(Vehicle).where(Vehicle.status==s)) for s in VehicleStatus}
    return {"role":user.role.name,"vehicle_counts":counts,"created_jobs":db.scalar(select(func.count()).select_from(Job).where(Job.status==JobStatus.CREATED)),"active_jobs":db.scalar(select(func.count()).select_from(Job).where(Job.status.in_([JobStatus.ASSIGNED,JobStatus.IN_PROGRESS])))}

@app.get("/api/v1/jobs")
def jobs(db:DB,user:Annotated[User,Depends(get_current_user)]):
    allowed={p.code for p in user.role.permissions}; q=select(Job).order_by(Job.created_at.desc())
    if "jobs.view.all" not in allowed:
        if "jobs.view.own" not in allowed: raise HTTPException(403,"Missing permission: jobs.view.all")
        q=q.where(Job.driver_id==user.employee_id)
    return [job_data(x) for x in db.scalars(q).all()]
@app.post("/api/v1/jobs",status_code=201)
def create_job(payload:JobInput,db:DB,user:Annotated[User,Depends(require_permission("jobs.create"))]):
    j=Job(id=f"JOB-{datetime.now():%Y%m%d}-{secrets.token_hex(3).upper()}",**payload.model_dump());db.add(j);audit(db,user,"CREATE","JOB",j.id);db.commit();return job_data(j)
@app.get("/api/v1/jobs/{job_id}")
def get_job(job_id:str,db:DB,user:Annotated[User,Depends(get_current_user)]):
    j=db.get(Job,job_id)
    if not j: raise HTTPException(404,"Job not found")
    if "jobs.view.all" not in {p.code for p in user.role.permissions} and not own_job(j,user): raise HTTPException(403,"Not your job")
    return job_data(j)
@app.post("/api/v1/jobs/{job_id}/cancel")
def cancel_job(job_id:str,db:DB,user:Annotated[User,Depends(require_permission("jobs.cancel"))]):
    j=db.get(Job,job_id)
    if not j: raise HTTPException(404,"Job not found")
    if j.status in [JobStatus.COMPLETED,JobStatus.CANCELLED]: raise HTTPException(409,"Job cannot be cancelled")
    if j.vehicle_id:
        v=db.get(Vehicle,j.vehicle_id);v.status=VehicleStatus.AVAILABLE;v.ready_from=j.origin;v.current_destination=None
    j.status=JobStatus.CANCELLED;audit(db,user,"CANCEL","JOB",j.id);db.commit();return job_data(j)

@app.get("/api/v1/dispatch/candidates")
def candidates(db:DB,origin:str="",employee_name:str="",vehicle_plate:str="",user:Annotated[User,Depends(require_permission("dispatch.view"))]=None):
    q=select(Vehicle).options(selectinload(Vehicle.employee)).where(Vehicle.status.in_([VehicleStatus.AVAILABLE,VehicleStatus.AVAILABLE_RETURN]))
    rows=[]
    for v in db.scalars(q).all():
        if origin and not ((v.status==VehicleStatus.AVAILABLE and v.ready_from==origin) or (v.status==VehicleStatus.AVAILABLE_RETURN and v.current_destination==origin)): continue
        if employee_name and employee_name.lower() not in v.employee.name.lower(): continue
        if vehicle_plate and vehicle_plate.lower() not in v.plate.lower(): continue
        rows.append({"vehicle_id":v.id,"vehicle_plate":v.plate,"employee_id":v.employee_id,"employee_name":v.employee.name,"operational_status":v.status.value,"ready_from":v.ready_from,"current_destination":v.current_destination,"candidate_type":"return" if v.status==VehicleStatus.AVAILABLE_RETURN else "available"})
    return {"items":rows,"total":len(rows)}
@app.post("/api/v1/dispatch/assign")
def assign(payload:AssignInput,db:DB,user:Annotated[User,Depends(require_permission("dispatch.assign"))]):
    with db.begin_nested():
        j=db.scalar(select(Job).where(Job.id==payload.job_id).with_for_update()); v=db.scalar(select(Vehicle).where(Vehicle.id==payload.vehicle_id).with_for_update()); e=db.get(Employee,payload.employee_id)
        if not j or not v or not e: raise HTTPException(404,"Job, driver, or vehicle not found")
        if j.status!=JobStatus.CREATED: raise HTTPException(409,"Job is not available")
        if not e.is_active or v.employee_id!=e.id or v.status not in [VehicleStatus.AVAILABLE,VehicleStatus.AVAILABLE_RETURN]: raise HTTPException(409,"Driver or vehicle is not available")
        j.driver_id=e.id;j.vehicle_id=v.id;j.assigned_at=datetime.now(timezone.utc);j.status=JobStatus.ASSIGNED;v.status=VehicleStatus.BUSY;v.ready_from=None;audit(db,user,"ASSIGN","JOB",j.id,{"vehicle_id":v.id,"driver_id":e.id})
    db.commit();return job_data(j)

@app.get("/api/v1/my/jobs")
def my_jobs(db:DB,user:Annotated[User,Depends(require_permission("jobs.view.own"))]): return [job_data(x) for x in db.scalars(select(Job).where(Job.driver_id==user.employee_id)).all()]
@app.post("/api/v1/my/check-in")
def check_in(db:DB,user:Annotated[User,Depends(require_permission("availability.check_in"))]): audit(db,user,"CHECK_IN","EMPLOYEE",user.employee_id);db.commit();return {"ok":True}
@app.post("/api/v1/my/ready")
def ready(payload:StatusInput,db:DB,user:Annotated[User,Depends(require_permission("availability.update.own"))]):
    v=db.scalar(select(Vehicle).where(Vehicle.employee_id==user.employee_id,Vehicle.is_primary==True));
    if not v or v.status==VehicleStatus.MAINTENANCE: raise HTTPException(409,"Vehicle cannot be set ready")
    v.status=VehicleStatus.AVAILABLE;v.ready_from=payload.ready_from;v.current_destination=None;audit(db,user,"READY","VEHICLE",v.id);db.commit();return {"status":v.status.value}
@app.post("/api/v1/my/not-ready")
def not_ready(db:DB,user:Annotated[User,Depends(require_permission("availability.update.own"))]):
    v=db.scalar(select(Vehicle).where(Vehicle.employee_id==user.employee_id,Vehicle.is_primary==True));
    if not v or v.status==VehicleStatus.BUSY: raise HTTPException(409,"Vehicle cannot be set not ready")
    v.status=VehicleStatus.NOT_READY;v.ready_from=None;audit(db,user,"NOT_READY","VEHICLE",v.id);db.commit();return {"status":v.status.value}
@app.post("/api/v1/my/jobs/{job_id}/start")
def start(job_id:str,db:DB,user:Annotated[User,Depends(require_permission("jobs.start.own"))]):
    j=db.get(Job,job_id)
    if not j or not own_job(j,user): raise HTTPException(404,"Assigned job not found")
    if j.status!=JobStatus.ASSIGNED: raise HTTPException(409,"Job cannot be started")
    j.status=JobStatus.IN_PROGRESS;j.started_at=datetime.now(timezone.utc);audit(db,user,"START","JOB",j.id);db.commit();return job_data(j)
@app.patch("/api/v1/my/jobs/{job_id}/destination")
def change_destination(job_id:str,payload:DestinationInput,db:DB,user:Annotated[User,Depends(require_permission("jobs.change_destination.own"))]):
    j=db.get(Job,job_id)
    if not j or not own_job(j,user) or j.status!=JobStatus.IN_PROGRESS: raise HTTPException(409,"Active assigned job required")
    j.destination=payload.destination;audit(db,user,"CHANGE_DESTINATION","JOB",j.id);db.commit();return job_data(j)
@app.post("/api/v1/my/jobs/{job_id}/close")
def close(job_id:str,db:DB,user:Annotated[User,Depends(require_permission("jobs.close.own"))]):
    j=db.get(Job,job_id)
    if not j or not own_job(j,user) or j.status!=JobStatus.IN_PROGRESS: raise HTTPException(409,"In-progress assigned job required")
    j.status=JobStatus.COMPLETED;j.completed_at=datetime.now(timezone.utc);v=db.get(Vehicle,j.vehicle_id);v.status=VehicleStatus.AVAILABLE_RETURN if j.job_type==JobType.ONE_WAY else VehicleStatus.AVAILABLE;v.current_destination=j.destination if j.job_type==JobType.ONE_WAY else None;v.ready_from=j.destination if j.job_type==JobType.ROUND_TRIP else None;audit(db,user,"CLOSE","JOB",j.id);db.commit();return job_data(j)

@app.get("/api/v1/employees")
def employees(db:DB,user:Annotated[User,Depends(require_permission("employees.view.all"))]): return [{"id":e.id,"name":e.name,"position":e.position,"phone":e.phone,"is_active":e.is_active} for e in db.scalars(select(Employee)).all()]
@app.get("/api/v1/vehicles")
def vehicles(db:DB,user:Annotated[User,Depends(require_permission("vehicles.view.all"))]): return [{"id":v.id,"plate":v.plate,"employee_id":v.employee_id,"status":v.status.value,"is_primary":v.is_primary,"ready_from":v.ready_from,"current_destination":v.current_destination} for v in db.scalars(select(Vehicle)).all()]
@app.get("/api/v1/roles")
def roles(db:DB,user:Annotated[User,Depends(require_permission("roles.view"))]): return [{"id":r.id,"name":r.name,"description":r.description,"users_count":len(r.users),"permissions":[p.code for p in r.permissions]} for r in db.scalars(select(Role).options(selectinload(Role.permissions),selectinload(Role.users))).all()]
@app.get("/api/v1/permissions")
def permissions(db:DB,user:Annotated[User,Depends(require_permission("permissions.view"))]): return [{"code":p.code,"module":p.module,"action":p.action,"scope":p.scope,"description":p.description} for p in db.scalars(select(Permission).order_by(Permission.code)).all()]
@app.get("/api/v1/audit-logs")
def logs(db:DB,user:Annotated[User,Depends(require_permission("audit_logs.view"))]): return [{"id":x.id,"action":x.action,"entity":x.entity,"entity_id":x.entity_id,"created_at":x.created_at.isoformat()} for x in db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)).all()]
