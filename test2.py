from multiprocessing import Pool


def main_fun(x):
    ...
    print(x, flush=True)

if __name__ == "__main__":
    with Pool(5) as pool:
        pool.map(main_fun,range(10000))
    pool.close()
    pool.join()