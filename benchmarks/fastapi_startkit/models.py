"""Standalone (no-FastAPI) setup for the FastAPI-Startkit ORM benchmark.

The FastAPI-Startkit ORM is an async-adapted MasoniteORM exposed as
``fastapi_startkit.masoniteorm``.  This module wires it up without booting a
full ``Application``: it does what ``DatabaseProvider.register()`` does (build a
``DatabaseManager`` and attach it to ``Model``) and installs the minimal global
container the connection factory needs.
"""
import logging
import os

from fastapi_startkit.container.container import Container
from fastapi_startkit.masoniteorm import Migrator, Model
from fastapi_startkit.masoniteorm.connections.factory import ConnectionFactory
from fastapi_startkit.masoniteorm.connections.manager import DatabaseManager

dbtype = os.environ.get("DBTYPE", "")
if dbtype == "postgres":
    _url = (
        f"postgresql+asyncpg://postgres:{os.environ.get('PASSWORD')}"
        f"@localhost:{os.environ.get('PGPORT', '5432')}/tbench"
    )
    _connection = {"driver": "postgres", "url": _url}
elif dbtype == "mysql":
    _url = (
        f"mysql+aiomysql://root:{os.environ.get('PASSWORD')}"
        f"@localhost:{os.environ.get('MYPORT', '3306')}/tbench"
    )
    _connection = {"driver": "mysql", "url": _url}
else:
    # The factory's build_url() assembles user:pwd@host:port and chokes on the
    # empty sqlite port, so sqlite must pass an explicit SQLAlchemy url.
    _connection = {
        "driver": "sqlite",
        "database": "/tmp/db.sqlite3",
        "url": "sqlite+aiosqlite:////tmp/db.sqlite3",
    }

DATABASE_CONFIG = {"default": dbtype or "sqlite", "connections": {dbtype or "sqlite": _connection}}


class _MinimalApp(Container):
    """Minimal container so ``app().is_testing()`` resolves inside the factory."""

    def is_testing(self) -> bool:
        return False


class Journal(Model):
    __table__ = "journal"


def _silence_sql_echo() -> None:
    # The factory hard-codes engine echo=True and re-sets the logger to INFO when
    # the engine is lazily created, so disabling the logger outright is the only
    # thing that survives.
    logging.getLogger("sqlalchemy.engine.Engine").disabled = True
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def setup() -> DatabaseManager:
    Container.set_instance(_MinimalApp())
    db = DatabaseManager(ConnectionFactory(), DATABASE_CONFIG)
    Model.db_manager = db
    Migrator.db_manager = db
    _silence_sql_echo()
    return db


async def create_tables(db: DatabaseManager) -> None:
    schema = db.get_schema_builder()
    await schema.drop_table_if_exists("journal")
    async with await schema.create("journal") as table:
        table.increments("id")
        table.integer("level")
        table.string("text")
        table.timestamps()
