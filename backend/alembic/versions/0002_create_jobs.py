"""create jobs table"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_create_jobs"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    job_source = postgresql.ENUM("EXTERNAL", "INTERNAL", name="jobsource")
    job_type = postgresql.ENUM("ONE_WAY", "ROUND_TRIP", name="jobtype")
    job_status = postgresql.ENUM("CREATED", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="jobstatus")
    for enum_type in (job_source, job_type, job_status):
        enum_type.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=30), primary_key=True),
        sa.Column("source", postgresql.ENUM(name="jobsource", create_type=False), nullable=False),
        sa.Column("origin", sa.String(length=120), nullable=False),
        sa.Column("destination", sa.String(length=120), nullable=False),
        sa.Column("pickup_date", sa.String(length=20), nullable=False),
        sa.Column("pickup_time", sa.String(length=10), nullable=False),
        sa.Column("customer_reference", sa.String(length=160)),
        sa.Column("notes", sa.String(length=1000)),
        sa.Column("job_type", postgresql.ENUM(name="jobtype", create_type=False), nullable=False),
        sa.Column("status", postgresql.ENUM(name="jobstatus", create_type=False), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("jobs")
    for enum_name in ("jobstatus", "jobtype", "jobsource"):
        postgresql.ENUM(name=enum_name).drop(op.get_bind(), checkfirst=True)