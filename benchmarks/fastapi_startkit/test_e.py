import os
import time
from random import randrange

from models import Journal

LEVEL_CHOICE = [10, 20, 30, 40, 50]
iters = int(os.environ.get("ITERATIONS", "1000"))


async def runtest(loopstr):
    start = time.time()
    count = 0
    for _ in range(iters // 10):
        for level in LEVEL_CHOICE:
            offset = randrange(iters - 20)
            res = await Journal.where("level", level).offset(offset).limit(20).get()
            count += len(res)
    now = time.time()
    print(f"FastAPI-Startkit{loopstr}, E: Rows/sec: {count / (now - start): 10.2f}")
