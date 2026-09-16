from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    Driver,
    Permission,
    Role,
    User,
    Vehicle,
    VehicleStatus,
)
from .security import hash_password


# =========================================================
# Permissions
# =========================================================

PERMISSIONS = [
    "dashboard.view",

    "users.view",
    "users.create",
    "users.update",
    "users.deactivate",

    "roles.view",
    "roles.manage",
    "permissions.view",
    "permissions.manage",

    "drivers.view.all",
    "drivers.view.own",
    "drivers.create",
    "drivers.update",
    "drivers.deactivate",

    "vehicles.view.all",
    "vehicles.view.own",
    "vehicles.create",
    "vehicles.update",
    "vehicles.deactivate",

    "availability.view.all",
    "availability.view.own",
    "availability.update.all",
    "availability.update.own",
    "availability.check_in",

    "jobs.view.all",
    "jobs.view.own",
    "jobs.create",
    "jobs.update",
    "jobs.cancel",
    "jobs.start.own",
    "jobs.close.own",
    "jobs.change_destination.own",

    "dispatch.view",
    "dispatch.assign",
    "dispatch.reassign",
    "dispatch.cancel",

    "evidence.view.all",
    "evidence.view.own",
    "evidence.upload.own",

    "job_history.view.all",
    "job_history.view.own",

    "reports.view",
    "reports.export",

    "settings.view",
    "settings.manage",

    "audit_logs.view",

    "profile.view.own",
    "profile.complete.own",
    "profile.update.own",
    "profile.update.all",
]


# =========================================================
# Role Permissions
# =========================================================

ROLE_CODES = {
    # ดูแลระบบทั้งหมด
    "ADMINISTRATOR": set(PERMISSIONS),

    # ผู้แจ้งงาน / จัดงาน / มอบหมายงาน
    "ADMIN": {
        p
        for p in PERMISSIONS
        if p not in {
            "roles.view",
            "roles.manage",
            "permissions.view",
            "permissions.manage",
            "settings.view",
            "settings.manage",
            "audit_logs.view",
            "users.create",
            "users.update",
            "users.deactivate",
        }
    },

    # ดู Dashboard + จัดการ ADMIN + Audit Logs
    "MANAGER": {
        "dashboard.view",

        "users.view",
        "users.create",
        "users.update",
        "users.deactivate",

        "drivers.view.all",

        "vehicles.view.all",
        "vehicles.create",
        "vehicles.update",
        "vehicles.deactivate",

        "availability.view.all",
        "availability.update.all",

        "jobs.view.all",
        "jobs.create",
        "jobs.update",
        "jobs.cancel",

        "dispatch.view",
        "dispatch.assign",
        "dispatch.reassign",
        "dispatch.cancel",

        "evidence.view.all",
        "job_history.view.all",

        "reports.view",
        "reports.export",

        "audit_logs.view",
    },

    # Driver
    "DRIVER": {
        "dashboard.view",

        "drivers.view.own",

        "vehicles.view.own",

        "availability.view.own",
        "availability.update.own",
        "availability.check_in",

        "jobs.view.own",
        "jobs.start.own",
        "jobs.close.own",
        "jobs.change_destination.own",

        "evidence.view.own",
        "evidence.upload.own",

        "job_history.view.own",

        "profile.view.own",
        "profile.complete.own",
        "profile.update.own",
    },
}


def seed_database(db: Session) -> None:
    # =========================================================
    # 1. Permissions
    # =========================================================

    permissions = {
        permission.code: permission
        for permission in db.scalars(select(Permission)).all()
    }

    for code in PERMISSIONS:
        if code not in permissions:
            parts = code.split(".")

            module = parts[0]
            action = parts[1] if len(parts) > 1 else code
            scope = parts[2] if len(parts) > 2 else None

            permissions[code] = Permission(
                id=code,
                code=code,
                module=module,
                action=action,
                scope=scope,
                description=code.replace(".", " "),
            )

            db.add(permissions[code])

    db.flush()

    # =========================================================
    # 2. Roles
    # =========================================================

    roles = {
        role.name: role
        for role in db.scalars(select(Role)).all()
    }

    for name, codes in ROLE_CODES.items():
        role = roles.get(name)

        if not role:
            role = Role(
                id=name,
                name=name,
                description=f"System {name} role",
                is_system_role=True,
            )

            db.add(role)

        role.permissions = [
            permissions[permission_code]
            for permission_code in sorted(codes)
        ]

        roles[name] = role

    db.flush()

    # =========================================================
    # 3. Drivers
    # =========================================================

    samples = [
        (
            "DRV-001",
            "D001",
            "Somchai",
            "Chai Dee",
            "081-000-1001",
            "70-1234",
            VehicleStatus.AVAILABLE,
            "Hat Yai",
            None,
        ),
        (
            "DRV-002",
            "D002",
            "Wichai",
            "Kabdee",
            "081-000-1002",
            "70-5678",
            VehicleStatus.BUSY,
            None,
            None,
        ),
        (
            "DRV-003",
            "D003",
            "Pracha",
            "Tangjai",
            "081-000-1003",
            "70-9999",
            VehicleStatus.AVAILABLE_RETURN,
            None,
            "Hat Yai",
        ),
    ]

    for (
        driver_pk,
        driver_code,
        first_name,
        last_name,
        phone,
        plate,
        vehicle_status,
        ready_from,
        current_destination,
    ) in samples:

        # -----------------------------------------------------
        # Driver
        # -----------------------------------------------------

        driver = db.get(Driver, driver_pk)

        if not driver:
            driver = Driver(
                id=driver_pk,
                driver_id=driver_code,
                position="DRIVER",
                is_active=True,
            )

            db.add(driver)
            db.flush()

        else:
            # Update existing driver
            driver.driver_id = driver_code
            driver.position = "DRIVER"
            driver.is_active = True

        # -----------------------------------------------------
        # Vehicle
        # -----------------------------------------------------

        vehicle = db.scalar(
            select(Vehicle).where(
                Vehicle.plate == plate
            )
        )

        if not vehicle:
            vehicle = Vehicle(
                id=f"V-{driver_code}",
                plate=plate,
                driver_id=driver.id,
                is_primary=True,
                status=vehicle_status,
                ready_from=ready_from,
                current_destination=current_destination,
            )

            db.add(vehicle)

        else:
            # Update existing vehicle
            vehicle.driver_id = driver.id
            vehicle.is_primary = True
            vehicle.status = vehicle_status
            vehicle.ready_from = ready_from
            vehicle.current_destination = current_destination

    db.flush()

    # =========================================================
    # 4. Users
    # =========================================================

    accounts = [
        {
            "id": "U-ADM-001",
            "email": "administrator@ntp-permpoon.com",
            "password": "admin123",
            "role": "ADMINISTRATOR",
            "driver_id": None,
            "first_name": "System",
            "last_name": "Administrator",
            "phone": None,
            "address": None,
            "profile_completed": True,
        },
        {
            "id": "U-OPS-001",
            "email": "admin@ntp-permpoon.com",
            "password": "admin123",
            "role": "ADMIN",
            "driver_id": None,
            "first_name": "System",
            "last_name": "Admin",
            "phone": None,
            "address": None,
            "profile_completed": True,
        },
        {
            "id": "U-MGR-001",
            "email": "manager@ntp-permpoon.com",
            "password": "manager123",
            "role": "MANAGER",
            "driver_id": None,
            "first_name": "System",
            "last_name": "Manager",
            "phone": None,
            "address": None,
            "profile_completed": True,
        },
        {
            "id": "U-DRV-001",
            "email": "driver@ntp-permpoon.com",
            "password": "driver123",
            "role": "DRIVER",
            "driver_id": "DRV-001",
            "first_name": "Somchai",
            "last_name": "Chai Dee",
            "phone": "081-000-1001",
            "address": None,
            "profile_completed": False,
        },
    ]

    # ---------------------------------------------------------
    # Load existing users
    # ---------------------------------------------------------

    existing_users = db.scalars(
        select(User)
    ).all()

    users_by_id = {
        user.id: user
        for user in existing_users
    }

    users_by_email = {
        user.email: user
        for user in existing_users
    }

    users_by_driver_id = {
        user.driver_id: user
        for user in existing_users
        if user.driver_id is not None
    }

    # ---------------------------------------------------------
    # Create / Update users
    # ---------------------------------------------------------

    for account in accounts:

        uid = account["id"]
        email = account["email"]
        driver_id = account["driver_id"]

        existing_user = (
            users_by_id.get(uid)
            or users_by_email.get(email)
            or (
                users_by_driver_id.get(driver_id)
                if driver_id
                else None
            )
        )

        # -----------------------------------------------------
        # Update existing user
        # -----------------------------------------------------

        if existing_user:
            existing_user.email = email

            # Reset password to seed password
            existing_user.password_hash = hash_password(
                account["password"]
            )

            existing_user.role_id = account["role"]
            existing_user.driver_id = driver_id
            existing_user.first_name = account["first_name"]
            existing_user.last_name = account["last_name"]
            existing_user.phone = account["phone"]
            existing_user.address = account["address"]
            existing_user.profile_completed = account[
                "profile_completed"
            ]

            continue

        # -----------------------------------------------------
        # Create new user
        # -----------------------------------------------------

        user = User(
            id=uid,
            email=email,
            password_hash=hash_password(
                account["password"]
            ),
            role_id=account["role"],
            driver_id=driver_id,
            first_name=account["first_name"],
            last_name=account["last_name"],
            phone=account["phone"],
            address=account["address"],
            profile_completed=account["profile_completed"],
        )

        db.add(user)

        # Keep dictionaries updated
        users_by_id[uid] = user
        users_by_email[email] = user

        if driver_id:
            users_by_driver_id[driver_id] = user

    # =========================================================
    # 5. Commit
    # =========================================================

    db.commit()
    