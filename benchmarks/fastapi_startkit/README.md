# FastAPI-Startkit ORM benchmark

Benchmarks the [FastAPI-Startkit ORM](https://fastapi-startkit.github.io/docs/database/) —
MasoniteORM adapted for async and exposed through the public
`fastapi_startkit.masoniteorm` API.

The benchmark uses the ORM **standalone**, the way the docs prescribe for non-web
usage: the framework boots as a **headless console application**. Constructing
`Application(providers=[(DatabaseProvider, DatabaseConfig)])` registers the ORM
(binds `db`/`schema` and attaches the model manager) with **no web server** —
`FastAPIProvider`/uvicorn are never involved. Only the documented public API is
used; no private internals and no `PYTHONPATH` tricks.

## Requirements

Install the framework with the `database` core extra plus the driver extra(s) for
the backend(s) you want to benchmark:

```sh
fastapi-startkit[database]   # SQLAlchemy async ORM
fastapi-startkit[postgres]   # asyncpg driver
fastapi-startkit[sqlite]     # aiosqlite driver
fastapi-startkit[mysql]      # aiomysql driver
```

For example, SQLite: `pip install "fastapi-startkit[database,sqlite]"`. It is
already declared in the repo's
`pyproject.toml`, so `make deps` / `pip install -e .` installs it. Once
`python -c "import fastapi_startkit.masoniteorm"` succeeds, no further setup is
needed.

## Running

```sh
# from this directory
./bench.sh
# or directly
DBTYPE=sqlite ITERATIONS=1000 python -m bench
```

Environment variables (shared with the other benchmarks):

- `DBTYPE` — `sqlite` (default), `postgres`, or `mysql`
- `ITERATIONS` — rows to insert (default `1000`)
- `PASSWORD`, `PGPORT`, `MYPORT` — credentials/ports for postgres/mysql

Expected output:

```
FastAPI-Startkit, A: Rows/sec:    XXXX.XX
```

## Scope

Currently implements the simple model (Test 1), operation **A** — single insert —
mirroring `benchmarks/django/simple/test_a.py`. Operations B–K and Tests 2–3 are
follow-ups.
