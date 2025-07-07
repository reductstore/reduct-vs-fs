import random
import time
import uuid
from datetime import datetime
from pathlib import Path
from time import sleep

import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

BLOB_SIZE = 50_000
BATCH_MAX_RECORDS = 80

BLOB_COUNT = min(1000, 1_000_000_000 // BLOB_SIZE)

CHUNK = random.randbytes(BLOB_SIZE)

HOST = "localhost"
CONNECTION = f"postgresql://postgres:postgres@{HOST}:5432"
HERE = Path(__file__).parent

def setup_database():
    con = psycopg2.connect(CONNECTION)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
    cur.execute(f"DROP DATABASE IF EXISTS benchmark")
    cur.execute(f"CREATE DATABASE benchmark")
    con.commit()
    con.close()


def get_or_create_file_path(timestamp: float, file_uid: str) -> Path:
    # make folder per second
    path = HERE / "files" / str(int(timestamp))
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{file_uid}.bin"

def write_to_timescale():
    setup_database()

    with psycopg2.connect(CONNECTION + "/benchmark") as con:
        with con.cursor() as cur:
            cur.execute(
                f"""CREATE TABLE data (
                       time TIMESTAMPTZ NOT NULL,
                       file_uid CHARACTER(36) NOT NULL);
                """
            )
            cur.execute("SELECT create_hypertable('data', by_range('time'))")
            con.commit()

            count = 0
            values = []
            for i in range(0, BLOB_COUNT):
                file_uid = str(uuid.uuid4())
                file_time = datetime.now()
                values.append((file_time, file_uid))

                # Write the file to disk
                file_path = get_or_create_file_path(file_time.timestamp(), file_uid)
                with open(file_path, "wb") as f:
                    f.write(CHUNK)

                sleep(0.000001)  # To avoid time collisions

                if len(values) >= BATCH_MAX_RECORDS:
                    psycopg2.extras.execute_values(
                        cur,
                        "INSERT INTO data (time, file_uid) VALUES %s;",
                        values,
                    )
                    values = []


                count += BLOB_SIZE


            if len(values) > 0:
                psycopg2.extras.execute_values(
                    cur,
                    "INSERT INTO data (time, file_uid) VALUES %s;",
                    values,
                )



    return count


def read_from_timescale(t1, t2):
    total_size = 0
    with psycopg2.connect(CONNECTION + "/benchmark") as con:
        with con.cursor() as cur:
            cur.execute(
                "SELECT time, file_uid FROM data WHERE time >= %s AND time < %s;",
                (datetime.fromtimestamp(t1), datetime.fromtimestamp(t2)),
            )
            while True:
                obj = cur.fetchone()
                if obj is None:
                    break
                file_time = obj[0].replace(tzinfo=None)  # Remove timezone info for consistency
                file_uid = obj[1]
                file_path = get_or_create_file_path(file_time.timestamp(), file_uid)
                with open(file_path, "rb") as f:
                    total_size += len(f.read())


    return total_size



if __name__ == "__main__":
    print(f"Chunk size={BLOB_SIZE / 1000_000} Mb, count={BLOB_COUNT}")
    ts = time.time()
    size = write_to_timescale()
    print(f"Write {size / 1000_000} Mb to TimescaleDB: {BLOB_COUNT / (time.time() - ts)} req/s")

    ts_read = time.time()
    size = read_from_timescale(ts, time.time())
    print(f"Read {size / 1000_000} Mb from TimescaleDB: {BLOB_COUNT / (time.time() - ts_read)} req/s")
