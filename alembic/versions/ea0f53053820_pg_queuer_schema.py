"""'pg queuer schema'

Revision ID: ea0f53053820
Revises: 64fc4e427bc4
Create Date: 2024-10-13 15:59:47.918428

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ea0f53053820"
down_revision: Union[str, None] = "64fc4e427bc4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create pgqueuer_status enum
    op.execute("CREATE TYPE pgqueuer_status AS ENUM ('queued', 'picked');")

    # Create pgqueuer table
    op.execute("""
    CREATE TABLE pgqueuer (
        id SERIAL PRIMARY KEY,
        priority INT NOT NULL,
        created TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
        updated TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
        heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
        status pgqueuer_status NOT NULL,
        entrypoint TEXT NOT NULL,
        payload BYTEA
    );
    """)

    # Create indexes on pgqueuer table
    op.execute("""
    CREATE INDEX pgqueuer_priority_id_id1_idx ON pgqueuer (priority ASC, id DESC)
        INCLUDE (id) WHERE status = 'queued';
    """)
    op.execute("""
    CREATE INDEX pgqueuer_updated_id_id1_idx ON pgqueuer (updated ASC, id DESC)
        INCLUDE (id) WHERE status = 'picked';
    """)

    # Create pgqueuer_statistics_status enum
    op.execute(
        "CREATE TYPE pgqueuer_statistics_status AS ENUM ('exception', 'successful', 'canceled');"
    )

    # Create pgqueuer_statistics table
    op.execute("""
    CREATE TABLE pgqueuer_statistics (
        id SERIAL PRIMARY KEY,
        created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT DATE_TRUNC('sec', NOW() at time zone 'UTC'),
        count BIGINT NOT NULL,
        priority INT NOT NULL,
        time_in_queue INTERVAL NOT NULL,
        status pgqueuer_statistics_status NOT NULL,
        entrypoint TEXT NOT NULL
    );
    """)

    # Create unique index on pgqueuer_statistics table
    op.execute("""
    CREATE UNIQUE INDEX pgqueuer_statistics_unique_count ON pgqueuer_statistics (
        priority,
        DATE_TRUNC('sec', created at time zone 'UTC'),
        DATE_TRUNC('sec', time_in_queue),
        status,
        entrypoint
    );
    """)

    # Create trigger function
    op.execute("""
    CREATE FUNCTION fn_pgqueuer_changed() RETURNS TRIGGER AS $$
    DECLARE
        to_emit BOOLEAN := false;  -- Flag to decide whether to emit a notification
    BEGIN
        -- Check operation type and set the emit flag accordingly
        IF TG_OP = 'UPDATE' AND OLD IS DISTINCT FROM NEW THEN
            to_emit := true;
        ELSIF TG_OP = 'DELETE' THEN
            to_emit := true;
        ELSIF TG_OP = 'INSERT' THEN
            to_emit := true;
        ELSIF TG_OP = 'TRUNCATE' THEN
            to_emit := true;
        END IF;

        -- Perform notification if the emit flag is set
        IF to_emit THEN
            PERFORM pg_notify(
                'ch_pgqueuer',
                json_build_object(
                    'channel', 'ch_pgqueuer',
                    'operation', lower(TG_OP),
                    'sent_at', NOW(),
                    'table', TG_TABLE_NAME,
                    'type', 'table_changed_event'
                )::text
            );
        END IF;

        -- Return appropriate value based on the operation
        IF TG_OP IN ('INSERT', 'UPDATE') THEN
            RETURN NEW;
        ELSIF TG_OP = 'DELETE' THEN
            RETURN OLD;
        ELSE
            RETURN NULL; -- For TRUNCATE and other non-row-specific contexts
        END IF;

    END;
    $$ LANGUAGE plpgsql;
    """)

    # Create trigger
    op.execute("""
    CREATE TRIGGER tg_pgqueuer_changed
    AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON pgqueuer
    EXECUTE FUNCTION fn_pgqueuer_changed();
    """)


def downgrade():
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS tg_pgqueuer_changed ON pgqueuer;")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS fn_pgqueuer_changed();")

    # Drop pgqueuer_statistics table and type
    op.execute("DROP TABLE IF EXISTS pgqueuer_statistics;")
    op.execute("DROP TYPE IF EXISTS pgqueuer_statistics_status;")

    # Drop indexes on pgqueuer table
    op.execute("DROP INDEX IF EXISTS pgqueuer_updated_id_id1_idx;")
    op.execute("DROP INDEX IF EXISTS pgqueuer_priority_id_id1_idx;")

    # Drop pgqueuer table and type
    op.execute("DROP TABLE IF EXISTS pgqueuer;")
    op.execute("DROP TYPE IF EXISTS pgqueuer_status;")
