"""FastAPI-Startkit ORM benchmark setup.

The FastAPI-Startkit ORM is MasoniteORM adapted for async, exposed through the
public ``fastapi_startkit.masoniteorm`` API. The framework boots as a headless
*console* application: constructing ``Application`` with only ``DatabaseProvider``
registers the ORM (binds ``db``/``schema`` and attaches the model manager) without
starting a web server — no ``FastAPIProvider`` and no uvicorn involved.
"""
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from fastapi_startkit import Application
from fastapi_startkit.masoniteorm import (
    DatabaseProvider,
    Model,
    MySQLConfig,
    PostgresConfig,
    SQLiteConfig,
)

dbtype = os.environ.get("DBTYPE", "") or "sqlite"

if dbtype == "postgres":
    _connection = PostgresConfig(
        driver="postgres",
        host="localhost",
        port=os.environ.get("PGPORT", "5432"),
        database="tbench",
        username="postgres",
        password=os.environ.get("PASSWORD", ""),
    )
elif dbtype == "mysql":
    _connection = MySQLConfig(
        driver="mysql",
        host="localhost",
        port=os.environ.get("MYPORT", "3306"),
        database="tbench",
        username="root",
        password=os.environ.get("PASSWORD", ""),
    )
else:
    dbtype = "sqlite"
    _connection = SQLiteConfig(
        driver="sqlite",
        database="/tmp/db.sqlite3",
        url="sqlite+aiosqlite:////tmp/db.sqlite3",
    )


@dataclass
class DatabaseConfig:
    default: str = dbtype
    connections: dict = field(default_factory=lambda: {dbtype: _connection})
    migrations: dict = field(
        default_factory=lambda: {"table": "migrations", "directory": "databases/migrations"}
    )


class Journal(Model):
    __table__ = "journal"


def _quiet_sql_echo() -> None:
    # The framework's engine factory hard-codes SQLAlchemy echo=True with no
    # config override. echo bypasses the logger's level, and SQLAlchemy attaches
    # its own stdout StreamHandler on first log because none is configured.
    # Pre-attaching a NullHandler both suppresses that fallback and swallows the
    # echo records, keeping benchmark output clean.
    logging.getLogger("sqlalchemy.engine.Engine").addHandler(logging.NullHandler())


def setup() -> Application:
    app = Application(
        base_path=Path(__file__).resolve().parent,
        providers=[(DatabaseProvider, DatabaseConfig)],
    )
    _quiet_sql_echo()
    return app


async def create_tables(app: Application) -> None:
    schema = app.make("schema")
    await schema.drop_table_if_exists("journal")
    async with await schema.create("journal") as table:
        table.increments("id")
        table.small_integer("level")
        table.string("text")
        table.timestamps()
        table.index("level")
        table.index("text")
