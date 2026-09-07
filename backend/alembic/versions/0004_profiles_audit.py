"""add profile fields and audit logs"""
from alembic import op
import sqlalchemy as sa

revision = "0004_profiles_audit"
down_revision = "0003_rbac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("address", sa.String(length=300), nullable=True))
    op.add_column("users", sa.Column("profile_completed_at", sa.DateTime(), nullable=True))
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("actor_user_id", sa.String(length=30), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("entity", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.String(length=80), nullable=True),
        sa.Column("metadata_json", sa.String(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_column("users", "profile_completed_at")
    op.drop_column("employees", "address")