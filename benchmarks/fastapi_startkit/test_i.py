import time
from random import choice

from fastapi_startkit.masoniteorm import DB
from models import Journal

LEVEL_CHOICE = [10, 20, 30, 40, 50]


async def runtest(loopstr):
    objs = await Journal.all()
    count = len(objs)

    start = time.time()
    await DB.begin_transaction()
    for obj in objs:
        obj.level = choice(LEVEL_CHOICE)
        obj.text = f"{obj.text} Update"
        await obj.save()
    await DB.commit()
    now = time.time()
    print(f"FastAPI-Startkit{loopstr}, I: Rows/sec: {count / (now - start): 10.2f}")
