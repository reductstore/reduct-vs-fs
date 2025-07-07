# reduct-vs-fs

Benchmarks ReducStore vs TimescaleDB+Filesystem
This repository contains benchmarks comparing the performance of ReductStore with TimescaleDB and a filesystem for storing blobs of various sizes.
The benchmarks are implemented in Python and utilize the `psycopg2` library for TimescaleDB and the `reduct-py` library for ReductStore.

Each benchmark consists of writing and reading blobs of different sizes. The size of the blobs can be adjusted by changing the `BLOB_SIZE` constant. 

# Running the Benchmarks

```bash
pip instalL -u -r requirements.txt
docker-compose up -d

python reduct_bench.py
python timescale_fs_bench.py
```

# Results


| Chunk Size | Operation | TimescaleDB + FS, blob/s | ReductStore, blob/s | ReductStore, % |
|------------|-----------|--------------------------|---------------------|----------------|
| 10 KB      | Write     | 2244                     | 3892                | +73%           |
|            | Read      | 13540                    | 31619               | +133%          |
| 50 KB      | Write     | 1020                     | 2052                | +101%          |
|            | Read      | 13062                    | 13887               | +6%            |
| 100 KB     | Write     | 2121                     | 2718                | +28%           |
|            | Read      | 12324                    | 7527                | -39%           |
| 500 KB     | Write     | 1543                     | 1963                | +27%           |
|            | Read      | 8677                     | 1967                | -77%           |
| 1 MB       | Write     | 1146                     | 2297                | +100%          |
|            | Read      | 5203                     | 1281                | -75%           |