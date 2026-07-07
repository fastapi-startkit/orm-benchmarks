import os
import time
from random import choice

from fastapi_startkit.masoniteorm import DB
from models import Journal, row

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("ITERATIONS", "1000"))


async def runtest(loopstr):
    start = time.time()
    await DB.begin_transaction()
    for i in range(count):
        await Journal.create(row({"level": choice(LEVEL_CHOICE), "text": f"Insert from B, item {i}"}))
    await DB.commit()
    now = time.time()
    print(f"FastAPI-Startkit{loopstr}, B: Rows/sec: {count / (now - start): 10.2f}")
