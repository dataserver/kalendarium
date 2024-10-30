from datetime import datetime

from constants.app_constants import DB_PATH
from models.database_context import DatabaseConnection
from models.event import Event


# Create table
def create_table():
    with DatabaseConnection(DB_PATH) as cursor:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS "events" (
            "id" INTEGER PRIMARY KEY,
            "title" TEXT NOT NULL,
            "description" TEXT DEFAULT NULL,
            "color" TEXT DEFAULT NULL,
            "created_at" TEXT NOT NULL,
            "updated_at" TEXT DEFAULT NULL,
            "scheduled_at" TEXT DEFAULT NULL
        );
        """
        drop_index_sql = 'DROP INDEX IF EXISTS "ix_events_scheduled";'
        create_index_sql = (
            'CREATE INDEX "ix_events_scheduled" ON "events" ("scheduled_at" ASC);'
        )
        cursor.execute(create_table_sql)
        cursor.execute(drop_index_sql)
        cursor.execute(create_index_sql)


# Insert
def insert(event: Event):
    with DatabaseConnection(DB_PATH) as cursor:
        created_at = event.created_at.strftime("%Y-%m-%d %H:%M:%S")
        sql = """
        INSERT INTO events (title, description, color, created_at, scheduled_at)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor.execute(
            sql,
            (
                event.title,
                event.description,
                event.color,
                created_at,
                event.scheduled_at,
            ),
        )


# Get all
def get_all():
    events = []
    with DatabaseConnection(DB_PATH) as cursor:
        cursor.execute("SELECT * FROM events;")
        events = cursor.fetchall()
    return events


# Get by ID
def get_event_by_id(id: int):
    with DatabaseConnection(DB_PATH) as cursor:
        cursor.execute("SELECT * FROM events WHERE id = ?;", (id,))
        return cursor.fetchone()


# Update
def update(event_id: int, event: Event):
    with DatabaseConnection(DB_PATH) as cursor:
        update_values = []
        sql = "UPDATE events SET "

        if event.title is not None:
            sql += "title = ?, "
            update_values.append(event.title)
        else:
            sql += "title = NULL, "

        if event.description is not None:
            sql += "description = ?, "
            update_values.append(event.description)
        else:
            sql += "description = NULL, "

        if event.color is not None:
            sql += "color = ?, "
            update_values.append(event.color)
        else:
            sql += "color = NULL, "

        if event.scheduled_at is not None:
            sql += "scheduled_at = ?, "
            update_values.append(event.scheduled_at.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            sql += "scheduled_at = NULL, "

        sql += "updated_at = ?, "
        update_values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql = sql.rstrip(", ")
        sql += " WHERE id = ?;"
        update_values.append(event_id)
        cursor.execute(sql, tuple(update_values))


# Delete
def delete_by_id(id: int):
    with DatabaseConnection(DB_PATH) as cursor:
        cursor.execute("DELETE FROM events WHERE id = ?;", (id,))


def get_for_month(dtime: datetime | None = None) -> list[Event]:
    events = []
    with DatabaseConnection(DB_PATH) as cursor:
        select_month = (
            dtime.strftime("%Y-%m")
            if isinstance(dtime, datetime)
            else datetime.now().strftime("%Y-%m")
        )
        cursor.execute(
            "SELECT * FROM events WHERE strftime('%Y-%m', scheduled_at) = ? ORDER BY scheduled_at ASC;",
            (select_month,),
        )
        rows = cursor.fetchall()
        for row in rows:
            events.append(Event(**row))
        return events


def get_for_day(dtime: datetime) -> list[Event]:
    events = []
    with DatabaseConnection(DB_PATH) as cursor:
        day = dtime.strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT * FROM events WHERE DATE(scheduled_at) = ? ORDER BY scheduled_at ASC;",
            (day,),
        )
        rows = cursor.fetchall()
        for row in rows:
            events.append(Event(**row))
    return events
