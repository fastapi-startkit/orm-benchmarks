import time

from models import Journal

LEVEL_CHOICE = [10, 20, 30, 40, 50]


async def runtest(loopstr):
    start = time.time()
    count = 0
    for _ in range(10):
        for level in LEVEL_CHOICE:
            rows = await Journal.where("level", level).get()
            res = [tuple(r.serialize().values()) for r in rows]
            count += len(res)
    now = time.time()
    print(f"FastAPI-Startkit{loopstr}, H: Rows/sec: {count / (now - start): 10.2f}")
