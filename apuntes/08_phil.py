from multiprocessing import Process
from multiprocessing import Condition, Semaphore, Lock
from multiprocessing import Array, Manager, Value
import time
import random

from monitorphil import Table, AnticheatTable

NPHIL = 5
K = 100



class CheatMonitor(object):
    def __init__(self):
        self.eating = Value('i', 0)
        self.thinking = Value('i', 0)
        self.mutex = Lock()
        self.other_eating = Condition(self.mutex)


    def wants_think(self, i):
        self.mutex.acquire()
        self.other_eating.wait_for(lambda : self.eating.value==2, 5) # timeout no se puede esperar de forma indefinida
        self.eating.value -= 1
        self.mutex.release()

    def is_eating(self, i):
        self.mutex.acquire()
        self.eating.value += 1
        self.other_eating.notify()
        self.mutex.release()




def delay(n):
    time.sleep(random.random()/n)


def philosopher_task(num:int, table: Table):
    while True:
        print (f"Philosofer {num} thinking")
        delay(3)
        print (f"Philosofer {num} wants to eat")
        table.wants_eat(num)
        if num == 1:
            print('......................................')
        print (f"Philosofer {num} eating")
        delay(3)
        table.wants_think(num)
        print (f"Philosofer {num} stops eating")

def philosopher_cheat(num:int, table: Table, cheat: CheatMonitor):
    while True:
        print (f"Cheat philosofer {num} thinking")
        delay(3)
        print (f"Cheat philosofer {num} wants to eat")
        table.wants_eat(num)
        cheat.is_eating(num)
        delay(3)
        print(f'Cheat philosofer {num} waiting')
        cheat.wants_think(num)
        table.wants_think(num)
        print (f"Philosofer {num} stops eating")

def main():
    manager = Manager()
    table = AnticheatTable(NPHIL, manager)
    cheat = CheatMonitor()
    philosofers = [Process(target=philosopher_task,
                        args=(i, table)) if i not in [0,2] \
                   else Process(target=philosopher_cheat,\
                                args=(i, table, cheat))
                   for i in range(NPHIL)]
    for i in range(NPHIL):
        philosofers[i].start()
    for i in range(NPHIL):
        philosofers[i].join()

if __name__ == '__main__':
    main()
