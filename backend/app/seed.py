from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Employee, Vehicle, VehicleStatus


def seed_database(session: Session) -> None:
    if session.scalar(select(Employee.id).limit(1)):
        return
    employees = [
        Employee(id="E001", name="สมชาย ใจดี", position="DRIVER", phone="081-000-1001"),
        Employee(id="E002", name="วิชัย ขับดี", position="DRIVER", phone="081-000-1002"),
        Employee(id="E003", name="ประชา ตั้งใจ", position="DRIVER", phone="081-000-1003"),
        Employee(id="E004", name="กมล ส่งไว", position="DRIVER", phone="081-000-1004"),
    ]
    session.add_all(employees)
    session.flush()
    session.add_all([
        Vehicle(id="V001", plate="70-1234", employee_id="E001", status=VehicleStatus.AVAILABLE, ready_from="หาดใหญ่"),
        Vehicle(id="V002", plate="70-5678", employee_id="E002", status=VehicleStatus.BUSY, current_destination="พัทลุง"),
        Vehicle(id="V003", plate="70-9999", employee_id="E003", status=VehicleStatus.AVAILABLE_RETURN, current_destination="หาดใหญ่"),
        Vehicle(id="V004", plate="70-1111", employee_id="E004", status=VehicleStatus.MAINTENANCE),
    ])
    session.commit()
