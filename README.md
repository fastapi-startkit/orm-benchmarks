# ORM Benchmark: FastAPI-Startkit vs SQLModel vs SQLAlchemy (async)

An apples-to-apples performance benchmark of three async Python ORMs across SQLite,
PostgreSQL 17, and MySQL 8.

**Tested ORMs:**

| ORM | Type | PostgreSQL | MySQL | SQLite |
|-----|------|:---:|:---:|:---:|
| [FastAPI-Startkit](https://fastapi-startkit.github.io/docs/database/) | async | asyncpg | aiomysql | aiosqlite |
| [SQLModel](https://github.com/tiangolo/sqlmodel) | async | asyncpg | aiomysql | aiosqlite |
| [SQLAlchemy ORM (async)](https://www.sqlalchemy.org/) | async | asyncpg | aiomysql | aiosqlite |

The FastAPI-Startkit ORM is MasoniteORM adapted for async, exposed through the public
`fastapi_startkit.masoniteorm` API. SQLModel is a thin layer over SQLAlchemy, so it is expected
to track closely with SQLAlchemy ORM (async).

## Methodology

- **Sequential, apples-to-apples:** every ORM is run with `CONCURRENTS=1`, i.e. one row/query at a
  time with no `asyncio.gather` fan-out. MasoniteORM (FastAPI-Startkit) routes through a single
  shared connection manager and cannot safely use a concurrent model, so `CONCURRENTS=1` is the
  only setting under which all three ORMs are directly comparable.
- **Model:** Test 1 — the simple model (4 fields: `id`, `timestamp`, `level` indexed, `text` indexed).
- **Iterations:** `ITERATIONS=100` per operation.
- **Environment:** Apple Silicon macOS, Python 3.13.7, `uvloop`. PostgreSQL 17 and MySQL 8 run in
  Docker; SQLite is a local file (`/tmp/db.sqlite3`). Figures are single-run and subject to
  run-to-run variance at this iteration count.
- Numbers are **Rows/sec** (higher is better).

## Operations

| Code | Operation | Description |
|------|-----------|-------------|
| A | Insert: Single | Insert one row at a time |
| B | Insert: Batch | Insert many rows in a single transaction |
| C | Insert: Bulk | Use bulk insert operations |
| D | Filter: Large | Fetch a large result set |
| E | Filter: Small | Fetch limit 20 with random offset |
| F | Get | Fetch a single row by primary key |
| G | Filter: dict | Fetch large result set as dicts |
| H | Filter: tuple | Fetch large result set as tuples |
| I | Update: Whole | Update all fields of a row |
| J | Update: Partial | Update a single field |
| K | Delete | Delete a single row |

`GM` = geometric mean across the available operations.

## Results

### SQLite

| ORM | A | B | C | D | E | F | G | H | I | J | K | GM |
|-----|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| FastAPI-Startkit | 1,825 | 4,540 | 53,594 | 22,518 | 14,894 | 2,863 | 22,872 | 23,012 | 4,345 | 4,529 | 4,596 | 8,650 |
| SQLModel | 1,712 | 6,270 | 6,443 | 155,157 | 44,741 | 5,194 | 139,025 | 258,892 | 2,844 | 3,088 | 2,925 | 13,301 |
| SQLAlchemy (async) | 1,917 | 9,011 | 9,504 | 176,493 | 53,332 | 5,129 | 179,372 | 264,619 | 2,896 | 3,188 | 2,967 | 15,241 |

### PostgreSQL 17

| ORM | A | B | C | D | E | F | G | H | I | J | K | GM |
|-----|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| FastAPI-Startkit | 467 | 3,016 | 25,715 | 17,640 | 4,710 | 1,039 | 15,654 | 14,514 | 2,614 | 3,601 | 3,645 | 4,694 |
| SQLModel | 246 | 4,910 | 6,802 | 66,662 | 23,397 | 3,774 | 127,944 | 263,599 | 2,322 | 2,679 | 2,608 | 8,861 |
| SQLAlchemy (async) | 645 | 18,424 | 24,576 | 140,911 | 35,796 | 4,165 | 165,252 | 213,190 | 2,259 | 2,632 | 2,631 | 13,773 |

### MySQL 8

| ORM | A | B | C | D | E | F | G | H | I | J | K | GM |
|-----|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| FastAPI-Startkit | 247 | 3,221 | 18,362 | 18,049 | 6,894 | 1,002 | 15,358 | 15,492 | N/A[^fsk-my] | N/A[^fsk-my] | 2,764 | 4,736[^fsk-gm] |
| SQLModel | 173 | 3,229 | 3,472 | 89,351 | 33,618 | 3,645 | 87,827 | 128,370 | 2,091 | 2,340 | 2,263 | 7,189 |
| SQLAlchemy (async) | 477 | 5,489 | 5,460 | 98,041 | 35,015 | 3,987 | 98,007 | 134,150 | 2,072 | 2,271 | 2,271 | 8,892 |

## Analysis

- **Reads** (`Filter: Large/dict/tuple`, D/G/H) are where SQLModel and SQLAlchemy (async) pull far
  ahead — their thin result mapping streams large result sets an order of magnitude faster than
  FastAPI-Startkit on every database.
- **Bulk insert** (C) is FastAPI-Startkit's standout: its single multi-row `INSERT` reaches ~54k
  rows/sec on SQLite and ~26k on PostgreSQL, several times the SQLAlchemy-based ORMs, which fall
  back to batched inserts here.
- **Single-row writes** (A, F, I, J, K) are close across all three, dominated by per-statement
  round-trip cost under sequential execution.
- **SQLModel vs SQLAlchemy (async):** SQLModel tracks SQLAlchemy closely, as expected for a thin
  wrapper, and trails it modestly on the heaviest read and batch-insert paths (Session/validation
  overhead).
- On **MySQL**, FastAPI-Startkit's `Update: Whole` and `Update: Partial` are unavailable — see the
  note below.

## Running the benchmark

```sh
# Clone and install
git clone https://github.com/fastapi-startkit/orm-benchmarks.git
cd orm-benchmarks
uv venv && source .venv/bin/activate
uv pip install -e .

# SQLite (default)
cd benchmarks && CONCURRENTS=1 sh bench.sh

# PostgreSQL
export DBTYPE=postgres PASSWORD=yourpassword PGPORT=5432
cd benchmarks && CONCURRENTS=1 sh bench.sh

# MySQL
export DBTYPE=mysql PASSWORD=yourpassword MYPORT=3306
cd benchmarks && CONCURRENTS=1 sh bench.sh
```

`bench.sh` runs all three ORMs across Test 1/2/3 and prints a combined table via `present.py`.
`bench.sh full` and `bench.sh extra` raise the iteration count (1,000 and 10,000 respectively).

[^fsk-my]: FastAPI-Startkit UPDATE operations are unavailable on MySQL due to an upstream
MasoniteORM MySQL UPDATE-grammar bug that qualifies columns with a bogus `users` table
(``UPDATE `journal` SET `users`.`level` … WHERE `users`.`id` = …`` → *Unknown column 'users.id'
in 'where clause'*). SQLite, PostgreSQL, and MySQL `Delete` are unaffected.

[^fsk-gm]: FastAPI-Startkit's MySQL geometric mean is computed over the 9 available operations
(A–H, K), excluding the two N/A updates.
