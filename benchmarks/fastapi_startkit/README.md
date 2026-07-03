# FastAPI-Startkit ORM benchmark

Benchmarks the [FastAPI-Startkit ORM](https://fastapi-startkit.github.io/docs/database/),
an async-adapted MasoniteORM exposed as `fastapi_startkit.masoniteorm`. This benchmark
uses the ORM **standalone** — no FastAPI app or `Application` boot is required.

## Requirements

Install the ORM (the `sqlite` extra pulls in the async SQLite driver + SQLAlchemy):

```sh
pip install "fastapi-startkit[sqlite]"
```

It is already declared in the repo's `pyproject.toml`, so `make deps` / `pip install -e .`
installs it. Once `python -c "import fastapi_startkit.masoniteorm"` succeeds, no further
setup is needed.

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
FastAPI-Startkit, A: Rows/sec:    1491.96
```

## Troubleshooting

If `import fastapi_startkit` fails even though the package is installed, an editable
install may be shadowing it with a stale/broken `.pth`. Either repair the install
(`pip install -e <valid checkout>`) or, as a temporary override, point `PYTHONPATH` at a
working source tree:

```sh
PYTHONPATH=/path/to/fastapi-startkit/src ./bench.sh
```

## Scope

Currently implements the simple model (Test 1), operation **A** — single insert —
mirroring `benchmarks/django/simple/test_a.py`. Operations B–K and Tests 2–3 are follow-ups.
