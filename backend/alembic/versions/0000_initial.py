"""Create initial delivery management schema.

Revision ID: 20260915_0001
Revises:
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0000_initial"
down_revision = None
branch_labels = None
depends_on = None

vehicle_status = postgresql.ENUM(
    "AVAILABLE", "BUSY", "NOT_READY", "MAINTENANCE", "AVAILABLE_RETURN",
    name="vehicle_status", create_type=False,
)
job_source = postgresql.ENUM(
    "EXTERNAL", "INTERNAL", name="job_source", create_type=False,
)
job_type = postgresql.ENUM(
    "ONE_WAY", "ROUND_TRIP", name="job_type", create_type=False,
)
job_status = postgresql.ENUM(
    "CREATED", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "CANCELLED",
    name="job_status", create_type=False,
)

def upgrade() -> None:
    bind = op.get_bind()

    for enum in (vehicle_status, job_source, job_type, job_status):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "roles",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255)),
        sa.Column("is_system_role", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("scope", sa.String(50)),
        sa.Column("description", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.String(50), nullable=False),
        sa.Column("permission_id", sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "drivers",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("driver_id", sa.String(50), nullable=False),
        sa.Column("position", sa.String(100)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("driver_id", name="uq_drivers_driver_id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role_id", sa.String(50), nullable=False),
        sa.Column("driver_id", sa.String(50)),
        sa.Column("first_name", sa.String(100)),
        sa.Column("last_name", sa.String(100)),
        sa.Column("phone", sa.String(30)),
        sa.Column("address", sa.String(300)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("profile_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("profile_completed_at", sa.DateTime(timezone=True)),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("driver_id", name="uq_users_driver_id"),
    )

    op.create_table(
        "vehicles",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("plate", sa.String(30), nullable=False),
        sa.Column("driver_id", sa.String(50), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", vehicle_status, nullable=False, server_default="NOT_READY"),
        sa.Column("ready_from", sa.String(120)),
        sa.Column("current_destination", sa.String(120)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("plate", name="uq_vehicles_plate"),
    )

    op.create_index(
        "uq_one_primary_vehicle_per_driver",
        "vehicles",
        ["driver_id"],
        unique=True,
        postgresql_where=sa.text("is_primary = TRUE"),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("source", job_source, nullable=False, server_default="EXTERNAL"),
        sa.Column("origin", sa.String(120), nullable=False),
        sa.Column("destination", sa.String(120), nullable=False),
        sa.Column("pickup_date", sa.String(20), nullable=False),
        sa.Column("pickup_time", sa.String(10), nullable=False),
        sa.Column("customer_reference", sa.String(160)),
        sa.Column("notes", sa.String(1000)),
        sa.Column("job_type", job_type, nullable=False, server_default="ONE_WAY"),
        sa.Column("status", job_status, nullable=False, server_default="CREATED"),
        sa.Column("driver_id", sa.String(50)),
        sa.Column("vehicle_id", sa.String(50)),
        sa.Column("created_by_user_id", sa.String(50), nullable=False),
        sa.Column("assigned_by_user_id", sa.String(50)),
        sa.Column("assigned_at", sa.DateTime(timezone=True)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["assigned_by_user_id"], ["users.id"], ondelete="RESTRICT"),
    )

    op.create_table(
        "job_evidence",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("job_id", sa.String(50), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_by_user_id", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], ondelete="RESTRICT"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("user_id", sa.String(50)),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100)),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("metadata_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )

    # Query-supporting indexes.
    op.create_index("ix_users_role_id", "users", ["role_id"])
    op.create_index("ix_users_driver_id", "users", ["driver_id"])

    op.create_index("ix_vehicles_driver_id", "vehicles", ["driver_id"])
    op.create_index("ix_vehicles_status", "vehicles", ["status"])
    op.create_index("ix_vehicles_current_destination", "vehicles", ["current_destination"])
    op.create_index("ix_vehicles_ready_from", "vehicles", ["ready_from"])
    op.create_index("ix_vehicles_status_current_destination", "vehicles", ["status", "current_destination"])
    op.create_index("ix_vehicles_status_ready_from", "vehicles", ["status", "ready_from"])

    op.create_index("ix_jobs_driver_id", "jobs", ["driver_id"])
    op.create_index("ix_jobs_vehicle_id", "jobs", ["vehicle_id"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_pickup_date", "jobs", ["pickup_date"])
    op.create_index("ix_jobs_origin", "jobs", ["origin"])
    op.create_index("ix_jobs_destination", "jobs", ["destination"])
    op.create_index("ix_jobs_created_at", "jobs", ["created_at"])
    op.create_index("ix_jobs_status_pickup_date", "jobs", ["status", "pickup_date"])

    op.create_index("ix_job_evidence_job_id", "job_evidence", ["job_id"])

    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_entity_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_entity_type", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_job_evidence_job_id", table_name="job_evidence")
    op.drop_table("job_evidence")

    op.drop_index("ix_jobs_status_pickup_date", table_name="jobs")
    op.drop_index("ix_jobs_created_at", table_name="jobs")
    op.drop_index("ix_jobs_destination", table_name="jobs")
    op.drop_index("ix_jobs_origin", table_name="jobs")
    op.drop_index("ix_jobs_pickup_date", table_name="jobs")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_index("ix_jobs_vehicle_id", table_name="jobs")
    op.drop_index("ix_jobs_driver_id", table_name="jobs")
    op.drop_table("jobs")

    op.drop_index("ix_vehicles_status_ready_from", table_name="vehicles")
    op.drop_index("ix_vehicles_status_current_destination", table_name="vehicles")
    op.drop_index("ix_vehicles_ready_from", table_name="vehicles")
    op.drop_index("ix_vehicles_current_destination", table_name="vehicles")
    op.drop_index("ix_vehicles_status", table_name="vehicles")
    op.drop_index("ix_vehicles_driver_id", table_name="vehicles")
    op.drop_index("uq_one_primary_vehicle_per_driver", table_name="vehicles")
    op.drop_table("vehicles")

    op.drop_table("users")
    op.drop_table("drivers")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")

    bind = op.get_bind()
    for enum in (job_status, job_type, job_source, vehicle_status):
        enum.drop(bind, checkfirst=True)
