import json
from datetime import datetime

from constants.app_constants import DB_PATH
from helpers.devtools import debug
from models.database_context import DatabaseConnection
from models.weatherforecast import WeatherForecast


# Create table
def create_table():
    with DatabaseConnection(DB_PATH) as cursor:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS "weatherforecasts" (
	        "id" INTEGER PRIMARY KEY,
            "date" TEXT NOT NULL,
            "json_obj" TEXT,
            "created_at" TEXT NOT NULL,
            "updated_at" TEXT
        );
        """
        drop_index_sql = 'DROP INDEX IF EXISTS "ix_weatherforecasts_date";'
        create_index_sql = 'CREATE INDEX "ix_weatherforecasts_date" ON "weatherforecasts" ("date" DESC);'
        cursor.execute(create_table_sql)
        cursor.execute(drop_index_sql)
        cursor.execute(create_index_sql)


# Insert
def insert(forecast: WeatherForecast):
    if forecast.json_obj:
        with DatabaseConnection(DB_PATH) as cursor:
            created_at = forecast.created_at.strftime("%Y-%m-%d %H:%M:%S")
            sql = """
            INSERT INTO weatherforecasts (date, json_obj, created_at)
            VALUES (?, ?, ?);
            """
            cursor.execute(
                sql,
                (forecast.date, forecast.json_obj.model_dump_json(), created_at),
            )


# Get all
def get_all():
    forecasts = []
    with DatabaseConnection(DB_PATH) as cursor:
        cursor.execute("SELECT * FROM weatherforecasts;")
        forecasts = cursor.fetchall()
    return forecasts


# Get by ID
def get_by_id(id: int):
    with DatabaseConnection(DB_PATH) as cursor:
        cursor.execute("SELECT * FROM weatherforecasts WHERE id = ?;", (id,))
        return cursor.fetchone()


# Update
def update(event_id: int, forecast: WeatherForecast):
    with DatabaseConnection(DB_PATH) as cursor:
        update_values = []
        sql = "UPDATE weatherforecasts SET "

        if forecast.date is not None:
            sql += "date = ?, "
            update_values.append(forecast.date)
        else:
            sql += "date = NULL, "

        if forecast.json_obj is not None:
            sql += "json_obj = ?, "
            update_values.append(forecast.json_obj)
        else:
            sql += "json_obj = NULL, "

        sql += "updated_at = ?, "
        update_values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql = sql.rstrip(", ")
        sql += " WHERE id = ?;"
        update_values.append(event_id)
        cursor.execute(sql, tuple(update_values))


# Delete
def delete_by_id(id: int):
    with DatabaseConnection(DB_PATH) as cursor:
        cursor.execute("DELETE FROM weatherforecasts WHERE id = ?;", (id,))


def get_for_month(dtime: datetime | None = None) -> list[WeatherForecast]:
    forecasts = []
    with DatabaseConnection(DB_PATH) as cursor:
        # Get the current year and month in YYYY-MM format
        select_month = (
            dtime.strftime("%Y-%m")
            if isinstance(dtime, datetime)
            else datetime.now().strftime("%Y-%m")
        )
        cursor.execute(
            "SELECT * FROM forecasts WHERE strftime('%Y-%m', date) = ? ORDER BY date ASC;",
            (select_month,),
        )
        rows = cursor.fetchall()
        for row in rows:
            forecasts.append(WeatherForecast(**row))
        return forecasts


def get_for_day(dtime: datetime) -> WeatherForecast | None:
    with DatabaseConnection(DB_PATH) as cursor:
        day = dtime.strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT * FROM weatherforecasts WHERE DATE(date) = ? ORDER BY date DESC LIMIT 1;",
            (day,),
        )
        row = cursor.fetchone()
        if row:
            return WeatherForecast(**row)
