import asyncio
import random
import time
from datetime import datetime

from reduct import Client as ReductClient, Batch

BLOB_SIZE = 10_000
BATCH_MAX_SIZE = 8_000_000
BATCH_MAX_RECORDS = 80

BLOB_COUNT = min(1000, 1_000_000_000 // BLOB_SIZE)

CHUNK = random.randbytes(BLOB_SIZE)

HOST = "localhost"


async def write_to_reduct():
    async with ReductClient(
            f"http://{HOST}:8383", api_token="reductstore"
    ) as reduct_client:
        count = 0
        bucket = await reduct_client.get_bucket("benchmark")
        batch = Batch()
        for i in range(0, BLOB_COUNT):
            batch.add(timestamp=datetime.now().timestamp(), data=CHUNK)
            await asyncio.sleep(0.000001)  # To avoid time collisions
            count += BLOB_SIZE

            if batch.size >= BATCH_MAX_SIZE or len(batch) >= BATCH_MAX_RECORDS:
                await bucket.write_batch("data", batch)
                batch.clear()

        if len(batch) > 0:
            await bucket.write_batch("data", batch)

        return count


async def read_from_reduct(t1, t2):
    async with ReductClient(
            f"http://{HOST}:8383", api_token="reductstore"
    ) as reduct_client:
        count = 0
        bucket = await reduct_client.get_bucket("benchmark")
        async for rec in bucket.query("data", t1, t2, ttl=90):
            count += len(await rec.read_all())
        return count


if __name__ == "__main__":
    print(f"Chunk size={BLOB_SIZE / 1000_000} Mb, count={BLOB_COUNT}")

    loop = asyncio.new_event_loop()
    ts = time.time()
    size = loop.run_until_complete(write_to_reduct())
    print(f"Write {size / 1000_000} Mb to ReductStore: {BLOB_COUNT / (time.time() - ts)} req/s")

    ts_read = time.time()
    size = loop.run_until_complete(read_from_reduct(ts, time.time()))
    print(f"Read {size / 1000_000} Mb from ReductStore: {BLOB_COUNT / (time.time() - ts_read)} req/s")
