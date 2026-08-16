"""add project owner foreign key

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-16 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    fks = [fk["name"] for fk in inspector.get_foreign_keys("projects")]

    if "fk_projects_owner_id_users" not in fks:
        with op.batch_alter_table("projects") as batch_op:
            batch_op.create_foreign_key(
                "fk_projects_owner_id_users",
                "users",
                ["owner_id"],
                ["id"],
                ondelete="CASCADE",
            )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    fks = [fk["name"] for fk in inspector.get_foreign_keys("projects")]

    if "fk_projects_owner_id_users" in fks:
        with op.batch_alter_table("projects") as batch_op:
            batch_op.drop_constraint(
                "fk_projects_owner_id_users",
                type_="foreignkey",
            )
