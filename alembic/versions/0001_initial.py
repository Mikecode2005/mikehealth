"""Initial migration.

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('doctor', 'nurse', 'patient', 'billing', name='userrole'), nullable=False),
        sa.Column('patient_id', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('ix_users_role_patient_id', 'users', ['role', 'patient_id'])

    # Patient records table
    op.create_table(
        'patient_records',
        sa.Column('patient_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('diagnoses', sa.String(2000), nullable=False, server_default='[]'),
        sa.Column('clinical_notes', sa.Text(), nullable=False, server_default=''),
        sa.Column('insurance_id', sa.String(100), nullable=True),
        sa.Column('balance_due', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('patient_id'),
        sa.UniqueConstraint('patient_id', name='uq_patient_records_patient_id'),
    )
    op.create_index('ix_patient_records_name', 'patient_records', ['name'])
    op.create_index('ix_patient_records_insurance_id', 'patient_records', ['insurance_id'])

    # Care team memberships table
    op.create_table(
        'care_team_memberships',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('patient_id', sa.String(36), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('assigned_by', sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patient_records.patient_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'patient_id', name='uq_care_team_user_patient'),
    )
    op.create_index('ix_care_team_user_patient', 'care_team_memberships', ['user_id', 'patient_id'])

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('patient_id', sa.String(36), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('ix_audit_logs_patient_timestamp', 'audit_logs', ['patient_id', 'timestamp'])
    op.create_index('ix_audit_logs_action_timestamp', 'audit_logs', ['action', 'timestamp'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('care_team_memberships')
    op.drop_table('patient_records')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS userrole")