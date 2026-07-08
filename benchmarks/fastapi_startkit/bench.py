#!/usr/bin/env python
import asyncio
import os

try:
    concurrents = int(os.environ.get("CONCURRENTS", "10"))

    if concurrents != 10:
        loopstr = f" C{concurrents}"
    else:
        loopstr = ""
    if os.environ.get("UVLOOP", ""):
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
finally:
    pass

import test_a
import test_b
import test_c
import test_d
import test_e
import test_f
import test_g
import test_h
import test_i
import test_j
import test_k
from models import create_tables, setup


TESTS = [
    ("A", test_a),
    ("B", test_b),
    ("C", test_c),
    ("D", test_d),
    ("E", test_e),
    ("F", test_f),
    ("G", test_g),
    ("H", test_h),
    ("I", test_i),
    ("J", test_j),
    ("K", test_k),
]


async def run_benchmarks():
    app = setup()
    await create_tables(app)
    for op, test in TESTS:
        try:
            await test.runtest(loopstr)
        except Exception as exc:
            # An operation the backend can't execute (e.g. the MasoniteORM MySQL
            # UPDATE-grammar bug on ops I/J) is reported N/A so the run continues
            # instead of aborting — otherwise later ops such as Delete (K) would
            # never be measured. Only the failure path is affected; timings for
            # successful ops are unchanged.
            print(f"FastAPI-Startkit{loopstr}, {op}: N/A ({type(exc).__name__})", flush=True)


asyncio.run(run_benchmarks())
