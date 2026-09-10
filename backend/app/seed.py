from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Employee, Permission, Role, User, Vehicle, VehicleStatus
from .security import hash_password

PERMISSIONS = [
 "dashboard.view","users.view","users.create","users.update","users.deactivate","roles.view","roles.manage","permissions.view","permissions.manage",
 "employees.view.all","employees.view.own","employees.create","employees.update","employees.deactivate","vehicles.view.all","vehicles.view.own","vehicles.create","vehicles.update","vehicles.deactivate",
 "availability.view.all","availability.view.own","availability.update.all","availability.update.own","availability.check_in","jobs.view.all","jobs.view.own","jobs.create","jobs.update","jobs.cancel","jobs.start.own","jobs.close.own","jobs.change_destination.own",
 "dispatch.view","dispatch.assign","dispatch.reassign","dispatch.cancel","evidence.view.all","evidence.view.own","evidence.upload.own","job_history.view.all","job_history.view.own","reports.view","reports.export","settings.view","settings.manage","audit_logs.view","profile.view.own","profile.complete.own","profile.update.all"]
ROLE_CODES = {
 "ADMINISTRATOR": set(PERMISSIONS),
 "ADMIN": {p for p in PERMISSIONS if p not in {"roles.view","roles.manage","permissions.view","permissions.manage","settings.view","settings.manage","audit_logs.view","users.create","users.update","users.deactivate"}},
 "MANAGER": {"dashboard.view","employees.view.all","vehicles.view.all","availability.view.all","jobs.view.all","dispatch.view","evidence.view.all","job_history.view.all","reports.view","profile.view.own"},
 "DRIVER": {"dashboard.view","employees.view.own","vehicles.view.own","availability.view.own","availability.update.own","availability.check_in","jobs.view.own","jobs.start.own","jobs.close.own","jobs.change_destination.own","evidence.view.own","evidence.upload.own","job_history.view.own","profile.view.own","profile.complete.own"},
}

def seed_database(db: Session) -> None:
    permissions = {x.code:x for x in db.scalars(select(Permission)).all()}
    for code in PERMISSIONS:
        if code not in permissions:
            module, action, *scope = code.split(".")
            permissions[code] = Permission(id=code, code=code, module=module, action=action, scope=scope[0] if scope else None, description=code.replace(".", " "))
            db.add(permissions[code])
    db.flush()
    roles = {x.name:x for x in db.scalars(select(Role)).all()}
    for name, codes in ROLE_CODES.items():
        role = roles.get(name) or Role(id=name, name=name, description=f"System {name} role")
        if name not in roles: db.add(role)
        role.permissions = [permissions[p] for p in codes]
        roles[name] = role
    db.flush()
    samples = [("E001","Somchai Chai Dee","081-000-1001","70-1234",VehicleStatus.AVAILABLE,"Hat Yai"),("E002","Wichai Kabdee","081-000-1002","70-5678",VehicleStatus.BUSY,None),("E003","Pracha Tangjai","081-000-1003","70-9999",VehicleStatus.AVAILABLE_RETURN,None)]
    for eid,name,phone,plate,status,ready in samples:
        employee = db.get(Employee,eid)
        if not employee:
            employee=Employee(id=eid,name=name,position="DRIVER",phone=phone); db.add(employee)
        if not db.scalar(select(Vehicle).where(Vehicle.plate==plate)):
            db.add(Vehicle(id="V"+eid[1:],plate=plate,employee_id=eid,is_primary=True,status=status,ready_from=ready,current_destination="Hat Yai" if status==VehicleStatus.AVAILABLE_RETURN else None))
    db.flush()
    accounts=[("U-ADM-001","administrator@ntp-permpoon.com","admin123","ADMINISTRATOR",None,True),("U-OPS-001","admin@ntp-permpoon.com","admin123","ADMIN",None,True),("U-MGR-001","manager@ntp-permpoon.com","manager123","MANAGER",None,True),("U-DRV-001","driver@ntp-permpoon.com","driver123","DRIVER","E001",False)]
    existing_users = db.scalars(select(User)).all()
    users_by_id = {user.id: user for user in existing_users}
    users_by_email = {user.email: user for user in existing_users}
    users_by_employee_id = {
        user.employee_id: user for user in existing_users if user.employee_id is not None
    }
    for uid,email,password,role,eid,complete in accounts:
        # Older databases can already have a driver linked to the employee
        # under a different seed email. Do not create a second user for that
        # employee; users.employee_id is unique.
        if not (users_by_id.get(uid) or users_by_email.get(email) or (eid and users_by_employee_id.get(eid))):
            db.add(User(id=uid,email=email,password_hash=hash_password(password),role_id=role,employee_id=eid,profile_completed=complete))
    db.commit()
