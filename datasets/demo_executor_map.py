from time import time, strftime
from concurrent import futures
from time import sleep


def display(*args):
    print(strftime('[%H:%M:%S]'), end=' ')
    print(*args)
    
    
def loiter(n):
    msg = '{}loiter({}): doing nothing for {}s...'
    display(msg.format('\t'*n, n, n))
    sleep(n)
    msg = '{}loiter({}): done'
    display(msg.format('\t'*n, n))
    return n * 10


def main():
    display('Script starting.')
    executor = futures.ThreadPoolExecutor(max_workers=3)
    results = executor.map(loiter, range(5))
    display('results:', results)
    display('Waiting for individual results:')
    for i, result in enumerate(results):    # 这个函数返回结果的顺序与调用开始的顺序一致
        display('result {}: {}'.format(i, result))
        

main()