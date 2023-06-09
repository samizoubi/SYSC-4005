"""
class buffer represents a buffer that processes the components after inspection before being sent to workstations


Authors
Peter Tanyous 101127203
Sara Shikhhassan 101142208
Sam Al Zoubi 101140949

Version 1 February 10, 2023

"""
from Component import Component

class Buffer:
    """
    Constructor
    """
    def __init__(self, component_type, workstation_id):
        self.capacity = 2 #represents the capacity of the buffer which is fixed to always 2
        self.buffer_type = component_type #represents the type of buffer: C1,C2,C3
        #occupancy represents how many components are 
        self.occupancy = 0
        self.workstation_id = workstation_id
        self.arrival_array_times = []
        self.departure_array_times = []
        
    """
    If buffer is not full add component and re-calculate occupancy
    clock is for the time at which the component came in 
    """   
    def increment_buffer(self, clock):
        if(self.occupancy < 2):
            self.occupancy = self.occupancy + 1
            self.arrival_array_times.append(clock)
            return True
        else:
            return False

    """
    If buffer is not empty remove component and re-calculate occupancy
    clock is for the time to which the component leaves.
    """         
    
    def decrement_buffer(self, clock):
        if(self.occupancy > 0):
            self.occupancy = self.occupancy -1 
            self.departure_array_times.append(clock)
            return True
        else:
            return False

    """
    returns the number of components in the buffer
    """

    def get_occupancy(self):
        return self.occupancy
    """
    returns the workstation id to which this buffer procession the components towards
    """
    def get_workstation(self):
        return self.workstation_id
    """
    returns the type of component that the buffer processes
    """
    def get_buffer_type(self):
        return self.buffer_type

    def print_arrival_departure_arrays(self):
        print(self.departure_array_times)
        print(self.arrival_array_times)

    def get_times_spent_in_buffer(self):
        diff = []
        for i in range(len(self.departure_array_times)):
            diff.append(self.departure_array_times[i] - self.arrival_array_times[i])
        return diff