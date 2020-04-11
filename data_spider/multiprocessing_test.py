import os
import time
from multiprocessing.pool import Pool


def mul_test(name, num):
    print('Run task  %s %s (%s) ...' % (name, num, os.getpid()))
    time.sleep(1)


if __name__ == '__main__':
    pool = Pool(4)
    name = "tom"
    for i in range(10):
        pool.apply_async(mul_test, args=(name, i,))

    pool.close()
    pool.join()
