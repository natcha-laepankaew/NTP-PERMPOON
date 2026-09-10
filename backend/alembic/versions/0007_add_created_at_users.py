"""align timestamp columns on users

The User model inherits Timestamped. Some existing databases recorded revision
0005 before its users.updated_at change was available, so reconcile both
timestamp columns here before SQLAlchemy loads User records.
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_add_created_at_users"
down_revision = "0006_created_at_emp_vehicle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns as nullable first so databases that already contain
    # users can be upgraded without violating the non-null constraint.
    existing_columns = {
        column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")
    }
    if "created_at" not in existing_columns:
        op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
    if "updated_at" not in existing_columns:
        op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))

    op.execute(
        """
        UPDATE users
        SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
            updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
        """
    )
    op.alter_column("users", "created_at", nullable=False)
    op.alter_column("users", "updated_at", nullable=False)


def downgrade() -> None:
    op.drop_column("users", "created_at")
