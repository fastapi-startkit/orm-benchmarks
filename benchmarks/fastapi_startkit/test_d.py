import time

from models import Journal

LEVEL_CHOICE = [10, 20, 30, 40, 50]


async def runtest(loopstr):
    start = time.time()
    count = 0
    for _ in range(10):
        for level in LEVEL_CHOICE:
            res = await Journal.where("level", level).get()
            count += len(res)
    now = time.time()
    print(f"FastAPI-Startkit{loopstr}, D: Rows/sec: {count / (now - start): 10.2f}")
