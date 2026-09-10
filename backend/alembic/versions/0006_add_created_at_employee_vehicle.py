"""add created_at to employees and vehicles"""

from alembic import op
import sqlalchemy as sa

# Keep this at or below 32 characters: existing Alembic installations commonly
# define alembic_version.version_num as VARCHAR(32).
revision = "0006_created_at_emp_vehicle"
down_revision = "0005_align_rbac_workflow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("employees", "vehicles"):
        op.add_column(
            table,
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )

        op.execute(
            f"""
            UPDATE {table}
            SET created_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
            """
        )

        op.alter_column(
            table,
            "created_at",
            nullable=False,
        )


def downgrade() -> None:
    op.drop_column("vehicles", "created_at")
    op.drop_column("employees", "created_at")
