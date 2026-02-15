"""Initial WMS schema

Revision ID: 20260215_0001
Revises: 
Create Date: 2026-02-15 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260215_0001"
down_revision = None
branch_labels = None
depends_on = None


location_type = sa.Enum("pick", "bulk", "staging", "dock", name="location_type", native_enum=False)
handling_unit_status = sa.Enum(
    "open", "sealed", "blocked", name="handling_unit_status", native_enum=False
)
mission_type = sa.Enum("move_hu", "move_item", name="mission_type", native_enum=False)
mission_state = sa.Enum(
    "draft", "assigned", "in_progress", "completed", "cancelled", name="mission_state", native_enum=False
)
inventory_movement_type = sa.Enum(
    "move", "adjustment", name="inventory_movement_type", native_enum=False
)
executor_type = sa.Enum("human", "agv", name="executor_type", native_enum=False)


def upgrade() -> None:
    op.create_table(
        "executors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("executor_type", executor_type, server_default="human", nullable=False),
        sa.Column("max_payload_kg", sa.Numeric(precision=10, scale=2), server_default="500", nullable=False),
        sa.Column("active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_executors_code"), "executors", ["code"], unique=False)
    op.create_index(op.f("ix_executors_id"), "executors", ["id"], unique=False)

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("uom", sa.String(length=32), server_default="ea", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
    )
    op.create_index(op.f("ix_items_id"), "items", ["id"], unique=False)
    op.create_index(op.f("ix_items_sku"), "items", ["sku"], unique=False)

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", location_type, server_default="bulk", nullable=False),
        sa.Column("active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_locations_code"), "locations", ["code"], unique=False)
    op.create_index(op.f("ix_locations_id"), "locations", ["id"], unique=False)

    op.create_table(
        "operators",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_operators_code"), "operators", ["code"], unique=False)
    op.create_index(op.f("ix_operators_id"), "operators", ["id"], unique=False)

    op.create_table(
        "handling_units",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hu_code", sa.String(length=64), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("status", handling_unit_status, server_default="open", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hu_code"),
    )
    op.create_index(op.f("ix_handling_units_hu_code"), "handling_units", ["hu_code"], unique=False)
    op.create_index(op.f("ix_handling_units_id"), "handling_units", ["id"], unique=False)

    op.create_table(
        "missions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mission_no", sa.String(length=64), nullable=False),
        sa.Column("type", mission_type, nullable=False),
        sa.Column("state", mission_state, server_default="draft", nullable=False),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_by_operator_id", sa.Integer(), nullable=False),
        sa.Column("assigned_executor_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_reason", sa.String(length=500), nullable=True),
        sa.CheckConstraint("priority >= 0", name="ck_missions_priority_non_negative"),
        sa.ForeignKeyConstraint(["assigned_executor_id"], ["executors.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_operator_id"], ["operators.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mission_no"),
    )
    op.create_index(op.f("ix_missions_id"), "missions", ["id"], unique=False)
    op.create_index(op.f("ix_missions_mission_no"), "missions", ["mission_no"], unique=False)

    op.create_table(
        "inventory_positions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hu_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("qty_on_hand", sa.Numeric(precision=18, scale=3), server_default="0", nullable=False),
        sa.Column("qty_reserved", sa.Numeric(precision=18, scale=3), server_default="0", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("qty_on_hand >= 0", name="ck_inventory_positions_on_hand_non_negative"),
        sa.CheckConstraint("qty_reserved >= 0", name="ck_inventory_positions_reserved_non_negative"),
        sa.CheckConstraint("qty_reserved <= qty_on_hand", name="ck_inventory_positions_reserved_le_on_hand"),
        sa.CheckConstraint("version >= 1", name="ck_inventory_positions_version_positive"),
        sa.ForeignKeyConstraint(["hu_id"], ["handling_units.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hu_id", "item_id", name="uq_inventory_positions_hu_item"),
    )
    op.create_index(op.f("ix_inventory_positions_id"), "inventory_positions", ["id"], unique=False)

    op.create_table(
        "mission_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mission_id", sa.Integer(), nullable=False),
        sa.Column("from_location_id", sa.Integer(), nullable=False),
        sa.Column("to_location_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("hu_id", sa.Integer(), nullable=True),
        sa.Column("qty", sa.Numeric(precision=18, scale=3), nullable=False),
        sa.Column("qty_done", sa.Numeric(precision=18, scale=3), server_default="0", nullable=False),
        sa.CheckConstraint("from_location_id != to_location_id", name="ck_mission_lines_source_destination_different"),
        sa.CheckConstraint("item_id IS NOT NULL OR hu_id IS NOT NULL", name="ck_mission_lines_item_or_hu_present"),
        sa.CheckConstraint("qty > 0", name="ck_mission_lines_qty_positive"),
        sa.CheckConstraint("qty_done <= qty", name="ck_mission_lines_qty_done_le_qty"),
        sa.CheckConstraint("qty_done >= 0", name="ck_mission_lines_qty_done_non_negative"),
        sa.ForeignKeyConstraint(["from_location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["hu_id"], ["handling_units.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mission_lines_id"), "mission_lines", ["id"], unique=False)

    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mission_line_id", sa.Integer(), nullable=True),
        sa.Column("movement_type", inventory_movement_type, server_default="move", nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("from_location_id", sa.Integer(), nullable=True),
        sa.Column("to_location_id", sa.Integer(), nullable=True),
        sa.Column("from_hu_id", sa.Integer(), nullable=True),
        sa.Column("to_hu_id", sa.Integer(), nullable=True),
        sa.Column("qty", sa.Numeric(precision=18, scale=3), nullable=False),
        sa.Column("executed_by_executor_id", sa.Integer(), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.CheckConstraint("qty > 0", name="ck_inventory_movements_qty_positive"),
        sa.ForeignKeyConstraint(["executed_by_executor_id"], ["executors.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["from_hu_id"], ["handling_units.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["from_location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["mission_line_id"], ["mission_lines.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_hu_id"], ["handling_units.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["to_location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index(op.f("ix_inventory_movements_id"), "inventory_movements", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_inventory_movements_id"), table_name="inventory_movements")
    op.drop_table("inventory_movements")

    op.drop_index(op.f("ix_mission_lines_id"), table_name="mission_lines")
    op.drop_table("mission_lines")

    op.drop_index(op.f("ix_inventory_positions_id"), table_name="inventory_positions")
    op.drop_table("inventory_positions")

    op.drop_index(op.f("ix_missions_mission_no"), table_name="missions")
    op.drop_index(op.f("ix_missions_id"), table_name="missions")
    op.drop_table("missions")

    op.drop_index(op.f("ix_handling_units_id"), table_name="handling_units")
    op.drop_index(op.f("ix_handling_units_hu_code"), table_name="handling_units")
    op.drop_table("handling_units")

    op.drop_index(op.f("ix_operators_id"), table_name="operators")
    op.drop_index(op.f("ix_operators_code"), table_name="operators")
    op.drop_table("operators")

    op.drop_index(op.f("ix_locations_id"), table_name="locations")
    op.drop_index(op.f("ix_locations_code"), table_name="locations")
    op.drop_table("locations")

    op.drop_index(op.f("ix_items_sku"), table_name="items")
    op.drop_index(op.f("ix_items_id"), table_name="items")
    op.drop_table("items")

    op.drop_index(op.f("ix_executors_id"), table_name="executors")
    op.drop_index(op.f("ix_executors_code"), table_name="executors")
    op.drop_table("executors")