"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 10
NPED = 5
TIME_CARS = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRGIAN = (30, 10) # normal 1s, 0.5s

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.patata = Value('i', 0)
        self.nped = Value('i', 0)
        self.ncarNorth = Value('i', 0)
        self.ncarSouth = Value('i', 0)
        self.north_car = Condition(self.mutex)
        self.south_car = Condition(self.mutex)
        self.ped = Condition(self.mutex)

    def are_no_car_north(self):
        return self.ncarNorth.value == 0
    
    def are_no_car_south(self):
        return self.ncarSouth.value == 0
    
    def are_no_pedestrian(self):
        return self.nped.value == 0
    
    def pass_ped(self):
        return self.are_no_car_north() and self.are_no_car_south()
    
    def pass_north(self):
        return self.are_no_pedestrian() and self.are_no_car_south()
    
    def pass_south(self):
        return self.are_no_pedestrian() and self.are_no_car_north()
    

    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        
        if direction == NORTH:
            self.north_car.wait_for(self.pass_north)
            self.ncarNorth.value += 1
        else:
            self.south_car.wait_for(self.pass_south)
            self.ncarSouth.value += 1
        
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        self.patata.value += 1
        
        if direction == NORTH:
            self.ncarNorth.value -= 1
            # Notificamos a los demás en caso de que no hayan coches norte:
            if self.ncarNorth.value == 0:
                self.south_car.notify_all()
                self.ped.notify_all()                    
        else:
            self.ncarSouth.value -= 1
            if self.ncarSouth.value == 0:
                self.north_car.notify_all()
                self.ped.notify_all()  
        
        self.mutex.release()
        

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        
        print(self.pass_ped == True)
        self.ped.wait_for(self.pass_ped)
        self.nped.value += 1
        
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        
        self.nped.value -= 1
        if self.nped.value == 0:
            self.north_car.notify_all()
            self.south_car.notify_all() 
            
        self.mutex.release()

    def __repr__(self) -> str:
        return f'Monitor: {self.patata.value}'

def delay_car_north(factor = 1) -> None:
    time.sleep(random.random()/factor)

def delay_car_south(factor = 1)-> None:
    time.sleep(random.random()/factor)

def delay_pedestrian(factor = 1) -> None:
    time.sleep(random.random()/factor)

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")



def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst:
        p.join()

def gen_cars(monitor) -> Monitor:
    cid = 0
    plst = []
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_CARS))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars = Process(target=gen_cars, args=(monitor,))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars.start()
    gped.start()
    gcars.join()
    gped.join()


if __name__ == '__main__':
    main()
