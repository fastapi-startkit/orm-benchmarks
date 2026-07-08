"""FastAPI-Startkit ORM benchmark setup.

The FastAPI-Startkit ORM is MasoniteORM adapted for async, exposed through the
public ``fastapi_startkit.masoniteorm`` API. The framework boots as a headless
*console* application: constructing ``Application`` with only ``DatabaseProvider``
registers the ORM (binds ``db``/``schema`` and attaches the model manager) without
starting a web server — no ``FastAPIProvider`` and no uvicorn involved.

``TEST`` selects the model shape, matching the other benchmarks:
1 = simple (4 fields), 2 = FK relations, 3 = wide model (32+ fields).
"""
import json
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

_CONNECTIONS = {
    # Postgres/MySQL configs ship a bogus default url (sqlite+aiosqlite://...),
    # and build_url() prefers url over host/port — so the url must be set
    # explicitly or the connection silently falls back to SQLite.
    "postgres": lambda: PostgresConfig(
        driver="postgres",
        host="localhost",
        port=os.environ.get("PGPORT", "5432"),
        database="tbench",
        username="postgres",
        password=os.environ.get("PASSWORD", ""),
        url=(
            f"postgresql+asyncpg://postgres:{os.environ.get('PASSWORD', '')}"
            f"@localhost:{os.environ.get('PGPORT', '5432')}/tbench"
        ),
    ),
    "mysql": lambda: MySQLConfig(
        driver="mysql",
        host="localhost",
        port=os.environ.get("MYPORT", "3306"),
        database="tbench",
        username="root",
        password=os.environ.get("PASSWORD", ""),
        url=(
            f"mysql+aiomysql://root:{os.environ.get('PASSWORD', '')}"
            f"@localhost:{os.environ.get('MYPORT', '3306')}/tbench"
        ),
    ),
    "sqlite": lambda: SQLiteConfig(
        driver="sqlite",
        database="/tmp/db.sqlite3",
        url="sqlite+aiosqlite:////tmp/db.sqlite3",
    ),
}

dbtype = os.environ.get("DBTYPE", "") or "sqlite"
dbtype = dbtype if dbtype in _CONNECTIONS else "sqlite"
_connection = _CONNECTIONS[dbtype]()


@dataclass
class DatabaseConfig:
    default: str = dbtype
    connections: dict = field(default_factory=lambda: {dbtype: _connection})
    migrations: dict = field(
        default_factory=lambda: {"table": "migrations", "directory": "databases/migrations"}
    )


TEST = int(os.environ.get("TEST", "1"))

# Wide-model (Test 3) column defaults, merged into every insert so the write
# exercises all columns. Series 1 & 3 carry values (NOT NULL); series 2 & 4 stay
# NULL, mirroring the SQLModel wide model.
_WIDE_TYPES = [
    # `double` not `float`: MasoniteORM's float() emits FLOAT(19,4), which
    # Postgres rejects as a syntax error; double -> DOUBLE PRECISION is portable.
    ("float", "double"),
    ("smallint", "small_integer"),
    ("int", "integer"),
    ("bigint", "big_integer"),
    ("char", "string"),
    ("text", "text"),
    ("decimal", "decimal"),
    ("json", "json"),
]
_WIDE_VALUES = {
    "float": 2.2,
    "smallint": 2,
    "int": 2000000,
    "bigint": 99999999,
    "char": "value1",
    "text": "Moo,Foo,Baa,Waa,Moo,Foo,Baa,Waa,Moo,Foo,Baa,Waa",
    "decimal": 2.2,
    "json": json.dumps({"a": 1, "b": "b", "c": [2], "d": {"e": 3}, "f": True}),
}
_WIDE_DEFAULTS = {}
if TEST == 3:
    for _grp in (1, 3):
        for _name, _val in _WIDE_VALUES.items():
            _WIDE_DEFAULTS[f"col_{_name}{_grp}"] = _val


def row(extra: dict) -> dict:
    """Insert payload: wide-model defaults (Test 3 only) merged with given fields."""
    return {**_WIDE_DEFAULTS, **extra}


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


def _add_common(table) -> None:
    table.increments("id")
    table.small_integer("level")
    table.string("text")


async def create_tables(app: Application) -> None:
    schema = app.make("schema")
    await schema.drop_table_if_exists("journal_related")
    await schema.drop_table_if_exists("journal")

    if TEST == 3:
        async with await schema.create("journal") as table:
            _add_common(table)
            for grp in (1, 2, 3, 4):
                nullable = grp in (2, 4)
                for suffix, method in _WIDE_TYPES:
                    col = getattr(table, method)(f"col_{suffix}{grp}")
                    if nullable:
                        col.nullable()
            table.timestamps()
            table.index("level")
            table.index("text")
        return

    async with await schema.create("journal") as table:
        _add_common(table)
        if TEST == 2:
            table.integer("parent_id").nullable()
        table.timestamps()
        table.index("level")
        table.index("text")

    if TEST == 2:
        async with await schema.create("journal_related") as table:
            table.integer("journal_id")
            table.integer("journal_from_id")
