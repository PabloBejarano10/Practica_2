from multiprocessing import Manager, Condition, Lock
from multiprocessing import Value

class Table(object):
    def __init__(self, size, manager):
        self.nphil = size
        self.phil = manager.list([False]*self.nphil)
        self.mutex = Lock()
        self.free_fork = Condition(self.mutex)


    def partners_not_eating(self, i):
        size = self.nphil
        return  not self.phil[(i-1)%size] and \
            not self.phil[(i+1) % size]

    def wants_eat(self, i):
        self.mutex.acquire()
        self.free_fork.wait_for(lambda: self.partners_not_eating(i))
        self.phil[i] = True
        self.mutex.release()

    def wants_think(self, i):
        self.mutex.acquire()
        self.phil[i] = False
        self.free_fork.notify_all()
        self.mutex.release()


class AnticheatTable(Table):
    def __init__(self, size, manager):
        super().__init__(size, manager)
        self.hungry = manager.list([False]*self.nphil)
        self.c_hungry = Condition(self.mutex)

    def wants_eat(self, i):
        self.mutex.acquire()
        self.c_hungry.wait_for(lambda : not self.hungry[ (i+1)%self.nphil])
        self.hungry[i] = True
        self.free_fork.wait_for(lambda: self.partners_not_eating(i))
        self.phil[i] = True
        self.hungry[i] = False
        self.c_hungry.notify_all()
        self.mutex.release()
