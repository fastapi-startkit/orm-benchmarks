import os
import time
from random import choice

from models import Journal, row

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("ITERATIONS", "1000"))


async def runtest(loopstr):
    start = time.time()
    await Journal.query().insert(
        [row({"level": choice(LEVEL_CHOICE), "text": f"Insert from C, item {i}"}) for i in range(count)]
    )
    now = time.time()
    print(f"FastAPI-Startkit{loopstr}, C: Rows/sec: {count / (now - start): 10.2f}")
