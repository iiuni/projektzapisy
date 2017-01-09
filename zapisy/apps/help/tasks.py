import time

def dummy_task(n):
    for i in range(n):
        print("Sleep %d" % i)
        time.sleep(1)
