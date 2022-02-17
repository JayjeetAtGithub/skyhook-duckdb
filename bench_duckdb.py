import os
import pyarrow.dataset as ds
import duckdb
import sys
import time
import json

import multiprocessing as mp


def drop_caches():
    os.system('sync')
    os.system('echo 3 > /proc/sys/vm/drop_caches')
    os.system('sync')


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("usage: ./bench.py <format(pq/sk)> <iterations> <dataset> <file>")
        sys.exit(0)

    fmt = str(sys.argv[1])
    iterations = int(sys.argv[2])
    directory = str(sys.argv[3])
    resultfile = str(sys.argv[4])

    if fmt == "sk":
        format_ = "skyhook"
    elif fmt == "pq":
        format_ = "parquet"

    selectivity = ["100", "10", "1"]
    data = dict()
    for per in selectivity:
        data[per] = list()
        for i in range(iterations):
            drop_caches()
            dataset = ds.dataset(directory, format=format_)
            conn = duckdb.connect()
            if per == "100":
                query = "SELECT * FROM dataset"
            if per == "10":
                query = "SELECT * FROM dataset WHERE total_amount > 27"
            if per == "1":
                query = "SELECT * FROM dataset WHERE total_amount > 69"

            start = time.time()
            record_batch_reader = conn.execute(query).fetch_record_batch(100000)
            chunk = record_batch_reader.read_next_batch()
            while chunk is not None:
                print(chunk.to_pandas())
                try:
                    chunk = record_batch_reader.read_next_batch()
                except:
                    break
            end = time.time()
            conn.close()
            data[per].append(end-start)
            print(end-start)

            with open(resultfile, 'w') as fp:
                json.dump(data, fp)
