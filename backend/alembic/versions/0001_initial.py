"""create employee and vehicle tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    status = postgresql.ENUM("AVAILABLE", "BUSY", "AVAILABLE_RETURN", "NOT_READY", "MAINTENANCE", name="vehiclestatus")
    status.create(op.get_bind(), checkfirst=True)
    op.create_table("employees", sa.Column("id", sa.String(length=20), primary_key=True), sa.Column("name", sa.String(length=120), nullable=False), sa.Column("position", sa.String(length=50), nullable=False), sa.Column("phone", sa.String(length=30), nullable=False))
    vehicle_status = postgresql.ENUM("AVAILABLE", "BUSY", "AVAILABLE_RETURN", "NOT_READY", "MAINTENANCE", name="vehiclestatus", create_type=False)
    op.create_table("vehicles", sa.Column("id", sa.String(length=20), primary_key=True), sa.Column("plate", sa.String(length=30), nullable=False, unique=True), sa.Column("employee_id", sa.String(length=20), sa.ForeignKey("employees.id")), sa.Column("status", vehicle_status, nullable=False), sa.Column("ready_from", sa.String(length=120)), sa.Column("current_destination", sa.String(length=120)))


def downgrade() -> None:
    op.drop_table("vehicles")
    op.drop_table("employees")
    postgresql.ENUM(name="vehiclestatus").drop(op.get_bind(), checkfirst=True)
