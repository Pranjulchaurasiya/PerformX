"""Add penalty_factor to goal_cycles

Revision ID: 001_penalty_factor
Revises: 
Create Date: 2025-05-16

Changes:
  - goal_cycles: add penalty_factor FLOAT NOT NULL DEFAULT 0.05
  - goal_sheets status enum: RESUBMITTED already handled in GoalStatus Python enum;
    this migration adds it to the DB enum type for PostgreSQL.
"""
from alembic import op
import sqlalchemy as sa


revision = "001_penalty_factor"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add penalty_factor column to goal_cycles
    op.add_column(
        "goal_cycles",
        sa.Column("penalty_factor", sa.Float(), nullable=False, server_default="0.05"),
    )

    # Add RESUBMITTED to the goalstatus enum in PostgreSQL
    # SQLAlchemy Enum in PG requires ALTER TYPE
    op.execute("ALTER TYPE goalstatus ADD VALUE IF NOT EXISTS 'resubmitted'")


def downgrade() -> None:
    op.drop_column("goal_cycles", "penalty_factor")
    # Note: PostgreSQL does not support removing enum values without recreating the type.
    # Downgrade leaves the enum value in place (safe — unused values are ignored).
