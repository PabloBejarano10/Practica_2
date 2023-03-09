from multiprocessing import Process, \
  BoundedSemaphore, Semaphore, Lock, Condition,\
  current_process, \
  Value, Array, Manager
from time import sleep
from random import random


N = 100
K = 10
NPROD = 3
NCONS = 3

def delay(factor = 3):
    sleep(random()/factor)

class PC_Monitor():
    def __init__(self, size: int):
        self.mutex = Lock()
        self.size = size
        self.manager = Manager()
        self.storage = self.manager.list()
        self.non_full = Condition(self.mutex)
        self.non_empty = Condition(self.mutex)

    def storage_non_full(self):
        return len(self.storage) < self.size

    def append(self, value: int):
        self.mutex.acquire()
        self.non_full.wait_for(self.storage_non_full)
        self.storage.append(value)
        print(f"monitor append:{len(self.storage)}")
        self.mutex.release()
        self.non_empty.notify()

    def storage_non_empty(self):
        return len(self.storage) > 0

    def get(self):
        self.mutex.acquire()
        self.non_empty.wait_for(self.storage_non_empty)
        value = self.storage.pop(0)
        self.non_full.notify()
        self.mutex.release()
        return value

def producer(monitor: PC_Monitor):
    data = 0
    while True:
        print(f"producer {current_process().name} produciendo")
        data += 1
        delay(6)
        monitor.append(data)
        print(f"producer {current_process().name} almacenado {data}")


def consumer(monitor: PC_Monitor):
    while True:
        print(f"consumer {current_process().name} desalmacenando")
        dato = monitor.get()
        print(f"consumer {current_process().name} consumiendo {dato}")
        delay(6)

def main():
    monitor = PC_Monitor(K)
    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(monitor, ))
                for i in range(NPROD) ]

    conslst = [ Process(target=consumer,
                        name=f"cons_{i}",
                        args=(monitor,))
                for i in range(NCONS) ]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()


if __name__ == '__main__':
    main()
