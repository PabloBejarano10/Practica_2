from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Value
from multiprocessing import current_process
import time, random

K=10
NR = 10
NW = 2

class Monitor():
    def __init__(self):
        self.nread = Value('i', 0)
        self.nwrite = Value('i', 0)
        self.nwrite_waiting = Value('i', 0)
        self.nread_waiting = Value('i', 0)
        self.turn = Value('i', 0)
        #turn 0 for writers
        #turn 1 for readers
        self.mutex = Lock()
        self.no_writers = Condition(self.mutex)
        self.nobody = Condition(self.mutex)

    def are_no_writers(self):
        return self.nwrite.value == 0 and \
            (self.turn.value == 1 or self.nwrite_waiting.value == 0)

    def want_read(self):
        self.mutex.acquire()
        self.nread_waiting.value += 1
        self.no_writers.wait_for(self.are_no_writers)
        self.nread_waiting.value -= 1
        self.nread.value += 1
        self.mutex.release()

    def stop_reading(self):
        self.mutex.acquire()
        self.nread.value -= 1
        self.turn.value = 0
        if self.nread.value == 0:
            self.nobody.notify()
        self.mutex.release()

    def are_nobody(self):
        return self.nread.value == 0 and \
            self.nwrite.value == 0 and \
            (self.turn.value == 0 or self.nread_waiting.value == 0)

    def want_write(self):
        self.mutex.acquire()
        self.nwrite_waiting.value += 1
        self.nobody.wait_for(self.are_nobody)
        self.nwrite_waiting.value -= 1
        self.nwrite.value += 1
        self.mutex.release()

    def stop_writing(self):
        self.mutex.acquire()
        self.nwrite.value -= 1
        self.turn.value = 1
        self.nobody.notify()
        self.no_writers.notify_all() # we must awake ALL readers
        # self.no_writers.notify() does not work
        self.mutex.release()

    def __str__(self):
        return f"M<r:{self.nread.value}, rw:{self.nread_waiting.value}, w:{self.nwrite.value}, ww:{self.nwrite_waiting}, turn:{self.turn.value}>"

def delay(d=3):
    time.sleep(random.random()/d)

def reader(monitor):
    for x in range(K):
        delay()
        print(f"reader {current_process().name} wants to read {x}. Status: {monitor}")
        monitor.want_read()
        print(f"reader {current_process().name} reading {x}. Status: {monitor}")
        delay()
        monitor.stop_reading()
        print(f"reader {current_process().name} stops reading {x}. Status: {monitor}")


def writer(monitor):
    for x in range(K):
        delay()
        print(f"writer {current_process().name} wants to write {x}. Status: {monitor}")
        monitor.want_write()
        print(f"writer {current_process().name} writing {x}. Status: {monitor}")
        delay()
        print(f"writer {current_process().name} stops writing {x}. Status: {monitor}")
        monitor.stop_writing()

def main():

    monitor = Monitor()
    readers = [Process(target=reader, name=f"r{i}", args=(monitor,)) \
               for i in range(NR)]
    writers = [Process(target=writer, name=f"w{i}", args=(monitor,)) \
               for i in range(NW)]

    for x in writers+readers:
        x.start()
    for x in writers+readers:
        x.join()

if __name__ == '__main__':
    main()
