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


