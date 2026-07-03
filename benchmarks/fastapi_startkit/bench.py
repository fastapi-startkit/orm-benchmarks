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
from models import create_tables, setup


async def run_benchmarks():
    app = setup()
    await create_tables(app)
    await test_a.runtest(loopstr)


asyncio.run(run_benchmarks())
