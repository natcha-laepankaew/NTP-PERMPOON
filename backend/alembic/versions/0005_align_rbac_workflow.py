"""align schema with the single-role dispatch domain"""
from alembic import op
import sqlalchemy as sa

revision = "0005_align_rbac_workflow"
down_revision = "0004_profiles_audit"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Existing MVP databases are upgraded in-place. New environments traverse this
    # migration chain before application seed data is inserted.
    op.execute("INSERT INTO roles (id, name, description, is_system_role) SELECT 'ADMINISTRATOR', 'ADMINISTRATOR', 'System administrator', TRUE WHERE NOT EXISTS (SELECT 1 FROM roles WHERE id = 'ADMINISTRATOR')")
    op.execute("INSERT INTO roles (id, name, description, is_system_role) SELECT 'DRIVER', 'DRIVER', 'Driver', TRUE WHERE NOT EXISTS (SELECT 1 FROM roles WHERE id = 'DRIVER')")
    op.execute("UPDATE user_roles SET role_id = 'ADMINISTRATOR' WHERE role_id = 'SUPER_ADMIN'")
    op.execute("UPDATE user_roles SET role_id = 'DRIVER' WHERE role_id = 'EMPLOYEE'")
    op.execute("UPDATE role_permissions SET role_id = 'ADMINISTRATOR' WHERE role_id = 'SUPER_ADMIN'")
    op.execute("UPDATE role_permissions SET role_id = 'DRIVER' WHERE role_id = 'EMPLOYEE'")
    op.execute("DELETE FROM roles WHERE id IN ('SUPER_ADMIN', 'EMPLOYEE')")
    op.add_column("users", sa.Column("role_id", sa.String(30), nullable=True))
    op.execute("UPDATE users SET role_id = COALESCE((SELECT role_id FROM user_roles WHERE user_id = users.id LIMIT 1), 'DRIVER')")
    op.create_foreign_key("fk_users_role", "users", "roles", ["role_id"], ["id"])
    op.alter_column("users", "role_id", nullable=False)
    op.drop_table("user_roles")
    for table in ("roles", "employees", "vehicles", "jobs"):
        op.add_column(table, sa.Column("updated_at", sa.DateTime(), nullable=True))
        op.execute(f"UPDATE {table} SET updated_at = CURRENT_TIMESTAMP")
        op.alter_column(table, "updated_at", nullable=False)
    op.add_column("roles", sa.Column("created_at", sa.DateTime(), nullable=True)); op.execute("UPDATE roles SET created_at = CURRENT_TIMESTAMP"); op.alter_column("roles", "created_at", nullable=False)
    op.add_column("permissions", sa.Column("created_at", sa.DateTime(), nullable=True)); op.execute("UPDATE permissions SET created_at = CURRENT_TIMESTAMP"); op.alter_column("permissions", "created_at", nullable=False)
    op.add_column("employees", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("vehicles", sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(), nullable=True))
    op.add_column("jobs", sa.Column("driver_id", sa.String(20), sa.ForeignKey("employees.id")))
    op.add_column("jobs", sa.Column("vehicle_id", sa.String(20), sa.ForeignKey("vehicles.id")))
    op.add_column("jobs", sa.Column("assigned_at", sa.DateTime())); op.add_column("jobs", sa.Column("started_at", sa.DateTime())); op.add_column("jobs", sa.Column("completed_at", sa.DateTime()))
    op.create_table("job_evidences", sa.Column("id", sa.String(40), primary_key=True), sa.Column("job_id", sa.String(30), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False), sa.Column("uploaded_by_user_id", sa.String(30), sa.ForeignKey("users.id"), nullable=False), sa.Column("file_name", sa.String(255), nullable=False), sa.Column("file_path", sa.String(500), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("uq_one_primary_vehicle_per_employee", "vehicles", ["employee_id"], unique=True, postgresql_where=sa.text("is_primary = TRUE"))

def downgrade() -> None:
    raise NotImplementedError("This production alignment migration is intentionally one-way")
