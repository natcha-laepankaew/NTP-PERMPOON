from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Employee, Permission, Role, User, Vehicle, VehicleStatus
from .security import hash_password

PERMISSION_DEFINITIONS = {
    "dashboard.view": ("dashboard", "view", None, "View dashboards"),
    "users.view": ("users", "view", None, "View users"), "users.create": ("users", "create", None, "Create users"), "users.update": ("users", "update", None, "Update users"), "users.delete": ("users", "delete", None, "Delete users"),
    "roles.view": ("roles", "view", None, "View roles"), "roles.manage": ("roles", "manage", None, "Manage roles"), "permissions.view": ("permissions", "view", None, "View permissions"), "permissions.manage": ("permissions", "manage", None, "Manage permissions"),
    "employees.view.all": ("employees", "view", "all", "View all employees"), "employees.view.own": ("employees", "view", "own", "View own employee profile"), "employees.create": ("employees", "create", None, "Create employees"), "employees.update": ("employees", "update", None, "Update employees"), "employees.delete": ("employees", "delete", None, "Deactivate employees"),
    "vehicles.view.all": ("vehicles", "view", "all", "View all vehicles"), "vehicles.view.own": ("vehicles", "view", "own", "View assigned vehicle"), "vehicles.create": ("vehicles", "create", None, "Create vehicles"), "vehicles.update": ("vehicles", "update", None, "Update vehicles"), "vehicles.delete": ("vehicles", "delete", None, "Deactivate vehicles"),
    "availability.view.all": ("availability", "view", "all", "View all availability"), "availability.view.own": ("availability", "view", "own", "View own availability"), "availability.update.all": ("availability", "update", "all", "Manage availability"), "availability.update.own": ("availability", "update", "own", "Update own availability"), "availability.check_in": ("availability", "check_in", "own", "Check in"),
    "jobs.view.all": ("jobs", "view", "all", "View all jobs"), "jobs.view.own": ("jobs", "view", "own", "View own jobs"), "jobs.create": ("jobs", "create", None, "Create jobs"), "jobs.update": ("jobs", "update", None, "Update jobs"), "jobs.delete": ("jobs", "delete", None, "Delete jobs"), "jobs.start.own": ("jobs", "start", "own", "Start own jobs"), "jobs.close.own": ("jobs", "close", "own", "Close own jobs"), "jobs.change_destination.own": ("jobs", "change_destination", "own", "Change own job destination"),
    "assignments.view.all": ("assignments", "view", "all", "View assignments"), "assignments.view.own": ("assignments", "view", "own", "View own assignments"), "assignments.assign": ("assignments", "assign", None, "Assign jobs"), "assignments.cancel": ("assignments", "cancel", None, "Cancel assignments"), "dispatch.view": ("dispatch", "view", None, "View dispatch board"), "dispatch.assign": ("dispatch", "assign", None, "Assign from dispatch board"),
    "evidence.view.all": ("evidence", "view", "all", "View all evidence"), "evidence.view.own": ("evidence", "view", "own", "View own evidence"), "evidence.upload.own": ("evidence", "upload", "own", "Upload own evidence"), "job_history.view.all": ("job_history", "view", "all", "View all job history"), "job_history.view.own": ("job_history", "view", "own", "View own job history"), "reports.view": ("reports", "view", None, "View reports"), "reports.export": ("reports", "export", None, "Export reports"), "settings.view": ("settings", "view", None, "View settings"), "settings.manage": ("settings", "manage", None, "Manage settings"), "audit_logs.view": ("audit_logs", "view", None, "View audit logs"), "profile.view.own": ("profile", "view", "own", "View own profile"), "profile.complete.own": ("profile", "complete", "own", "Complete first login profile"), "profile.update.all": ("profile", "update", "all", "Update profiles"),
}
ROLE_DESCRIPTIONS = {"SUPER_ADMIN": "Full system control", "ADMIN": "Create, update, assign and manage operations", "MANAGER": "View-only operations access", "EMPLOYEE": "Own profile, availability and jobs only"}
ROLE_PERMISSIONS = {
    "SUPER_ADMIN": set(PERMISSION_DEFINITIONS),
    "ADMIN": {code for code in PERMISSION_DEFINITIONS if code not in {"users.view", "users.create", "users.update", "users.delete", "roles.view", "roles.manage", "permissions.view", "permissions.manage", "settings.view", "settings.manage", "audit_logs.view"}},
    "MANAGER": {"dashboard.view", "employees.view.all", "vehicles.view.all", "availability.view.all", "jobs.view.all", "assignments.view.all", "dispatch.view", "evidence.view.all", "job_history.view.all", "reports.view", "profile.view.own"},
    "EMPLOYEE": {"dashboard.view", "employees.view.own", "vehicles.view.own", "availability.view.own", "availability.update.own", "availability.check_in", "jobs.view.own", "jobs.start.own", "jobs.close.own", "jobs.change_destination.own", "assignments.view.own", "evidence.view.own", "evidence.upload.own", "job_history.view.own", "profile.view.own", "profile.complete.own"},
}


def seed_database(session: Session) -> None:
    employees = seed_employees(session)
    seed_roles_and_permissions(session)
    seed_users(session, employees)
    session.commit()


def seed_employees(session: Session) -> dict[str, Employee]:
    existing = {employee.id: employee for employee in session.scalars(select(Employee)).all()}
    for employee_id, name, position, phone in [("E001", "สมชาย ใจดี", "DRIVER", "081-000-1001"), ("E002", "วิชัย ขับดี", "DRIVER", "081-000-1002"), ("E003", "ประชา ตั้งใจ", "DRIVER", "081-000-1003"), ("E004", "กมล ส่งไว", "DRIVER", "081-000-1004")]:
        if employee_id not in existing:
            existing[employee_id] = Employee(id=employee_id, name=name, position=position, phone=phone)
            session.add(existing[employee_id])
    session.flush()
    if not session.scalar(select(Vehicle.id).limit(1)):
        session.add_all([Vehicle(id="V001", plate="70-1234", employee_id="E001", status=VehicleStatus.AVAILABLE, ready_from="หาดใหญ่"), Vehicle(id="V002", plate="70-5678", employee_id="E002", status=VehicleStatus.BUSY, current_destination="พัทลุง"), Vehicle(id="V003", plate="70-9999", employee_id="E003", status=VehicleStatus.AVAILABLE_RETURN, current_destination="หาดใหญ่"), Vehicle(id="V004", plate="70-1111", employee_id="E004", status=VehicleStatus.MAINTENANCE)])
    return existing


def seed_roles_and_permissions(session: Session) -> None:
    permissions = {item.code: item for item in session.scalars(select(Permission)).all()}
    for code, (module, action, scope, description) in PERMISSION_DEFINITIONS.items():
        if code not in permissions:
            permissions[code] = Permission(id=code, code=code, module=module, action=action, scope=scope, description=description)
            session.add(permissions[code])
    session.flush()
    roles = {item.name: item for item in session.scalars(select(Role)).all()}
    for name, description in ROLE_DESCRIPTIONS.items():
        if name not in roles:
            roles[name] = Role(id=name, name=name, description=description, is_system_role=True)
            session.add(roles[name])
        roles[name].permissions = [permissions[code] for code in ROLE_PERMISSIONS[name]]
    session.flush()


def seed_users(session: Session, employees: dict[str, Employee]) -> None:
    roles = {item.name: item for item in session.scalars(select(Role)).all()}
    users = {item.email: item for item in session.scalars(select(User)).all()}
    for user_id, email, password, role_name, employee_id in [("U-SA-001", "superadmin@ntp-permpoon.com", "superadmin123", "SUPER_ADMIN", None), ("U-AD-001", "admin@ntp-permpoon.com", "admin123", "ADMIN", None), ("U-MG-001", "manager@ntp-permpoon.com", "manager123", "MANAGER", None), ("U-EM-001", "employee@ntp-permpoon.com", "employee123", "EMPLOYEE", "E001")]:
        user = users.get(email)
        if not user:
            user = User(id=user_id, email=email, password_hash=hash_password(password), employee_id=employee_id, profile_completed=True)
            session.add(user)
        user.roles = [roles[role_name]]
        if employee_id:
            user.employee = employees[employee_id]
