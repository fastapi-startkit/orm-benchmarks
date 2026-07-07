import time

from fastapi_startkit.masoniteorm import DB
from models import Journal


async def runtest(loopstr):
    objs = await Journal.all()
    count = len(objs)

    start = time.time()
    await DB.begin_transaction()
    for obj in objs:
        await Journal.where("id", obj.id).delete()
    await DB.commit()
    now = time.time()
    print(f"FastAPI-Startkit{loopstr}, K: Rows/sec: {count / (now - start): 10.2f}")
