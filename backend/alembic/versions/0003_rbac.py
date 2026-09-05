"""add RBAC users roles and permissions"""
from alembic import op
import sqlalchemy as sa

revision = "0003_rbac"
down_revision = "0002_create_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("roles", sa.Column("id", sa.String(30), primary_key=True), sa.Column("name", sa.String(30), nullable=False, unique=True), sa.Column("description", sa.String(240), nullable=False), sa.Column("is_system_role", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("permissions", sa.Column("id", sa.String(80), primary_key=True), sa.Column("code", sa.String(120), nullable=False, unique=True), sa.Column("module", sa.String(50), nullable=False), sa.Column("action", sa.String(40), nullable=False), sa.Column("scope", sa.String(20)), sa.Column("description", sa.String(240), nullable=False))
    op.create_table("users", sa.Column("id", sa.String(30), primary_key=True), sa.Column("email", sa.String(160), nullable=False, unique=True), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("profile_completed", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("employee_id", sa.String(20), sa.ForeignKey("employees.id"), unique=True))
    op.create_table("user_roles", sa.Column("user_id", sa.String(30), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("role_id", sa.String(30), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("role_permissions", sa.Column("role_id", sa.String(30), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True), sa.Column("permission_id", sa.String(80), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True))


def downgrade() -> None:
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("permissions")
    op.drop_table("roles")
