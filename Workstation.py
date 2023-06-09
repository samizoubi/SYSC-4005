"""
class workstation represents a workstation that receives components from buffers to make the product
This class will be used to simulate the 3 workstations in the manufacturing facility


Authors
Peter Tanyous 101127203
Sara Shikhhassan 101142208
Sam Al Zoubi 101140949

Version 1 February 10, 2023

"""
from Buffer import Buffer
from Component import Component

class Workstation:
    """
    Constructor
    """
    def __init__(self, id, buffersList, ):
        self.id = id #workstation unique id
        self.buffers = buffersList #list of buffers assigned to a workstation
        self.blocked = False #holds the status of the workstation to differentiate between busy and idle
        self.busy = False
        self.status = "Waiting for Arrival Event"
        self.products_count = 0

    """
    returns true if all components required to make the product are available in the buffers

    """
    def components_available(self):
        available = True
        for buffer in self.buffers:
            if buffer.get_occupancy() == 0:
                available = False
            else:
                pass
        return available
    
    def set_busy(self,busy_status):
        self.busy = busy_status

    def is_busy(self):
        return self.busy

    def update_workstation_status(self):
        if self.is_blocked():
            self.status = "Blocked"
        elif self.is_busy():
            self.status =  "Working"
        else: 
            self.status = "Waiting for Arrival Event"

    def set_status(self, new_status):
        self.status = new_status
    
    def get_status(self):
        return self.status



    """
    makes a product using the components in the buffer (if the components are available in the buffer)
    """
    def make_product(self, clock):
        if(self.components_available() == True):
            self.blocked = False
            for buffer in self.buffers:
                buffer.decrement_buffer(clock)
            # self.products_count = self.products_count + 1
            return True
        self.blocked = True
        return False

    def get_products_count(self):
        return self.products_count

    def increment_product_count(self):
        self.products_count = self.products_count + 1

    def is_blocked(self):
        return self.blocked
    
    def get_ID(self):
        return self.id