"""add unique project requirement capability

Revision ID: f7df2db5708d
Revises: 21b2ae104f6f
Create Date: 2026-08-12 22:20:56.872584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7df2db5708d'
down_revision: Union[str, None] = '21b2ae104f6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("project_requirements") as batch_op:
        batch_op.create_unique_constraint(
            "uq_project_requirement",
            ["project_id", "capability_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("project_requirements") as batch_op:
        batch_op.drop_constraint(
            "uq_project_requirement",
            type_="unique",
        )
