"""
Class inspector represents an inspector for certain component types who runs inspections before 
adding the components to the buffers at workstations. The inspector determines which buffers to send
components to and check if the buffer is unable to conduct inspections if blocked

Authors
Peter Tanyous 101127203
Sara Shikhhassan 101142208
Sam Al Zoubi 101140949

Version 1 February 10, 2023

"""
from Buffer import Buffer
from Component import Component

class Inspector:
    """
    Constructor
    """
    def __init__(self, id, buffers, component_type):
        self.id = id #inspector's id to identify whether it is inspector I1 or I2
        self.component = component_type #represents the component type to which the inspector is responsible for
        self.buffers = buffers
        self.blocked = False
        self.busy = False
        self.status = "Waiting for Arrival Event"
        self.next_component_to_make = None

    def set_next_component_to_make(self, comp):
        self.next_component_to_make = comp
    
    def get_next_component_to_make(self):
        return self.next_component_to_make

    def set_busy(self,busy_status):
        self.busy = busy_status
    def is_busy(self):
        return self.busy

    def update_inspector_status(self):
        if self.is_blocked():
            self.status = "Blocked"
        elif self.is_busy():
            self.status ="Inspecting"
        else: 
            self.status = "Waiting for Arrival Event"

    def set_status(self, new_status):
        self.status = new_status

    def get_status(self):
        return self.status 

    def send_target_buffer(self, input_component, clock):
        if (len(self.component) == 1): #inspector is responsible only for one component (first inspector who is responsible for C1, there shall be three buffers in this inspector's list)
            first_occupancy = self.buffers[0].get_occupancy()
            second_occupancy = self.buffers[1].get_occupancy()
            third_occupancy = self.buffers[2].get_occupancy()
            if(first_occupancy == 2 and second_occupancy ==2 and third_occupancy == 2):
                self.blocked = True
                return False
            elif(first_occupancy == second_occupancy == third_occupancy):
                iteration_number = 1
                for buffer in self.buffers: #if there is a tie it goes through the buffer and adds the component to them as per the priorities
                    if buffer.get_workstation() == iteration_number:
                        if(buffer.get_occupancy() < 2):
                            buffer.increment_buffer(clock)
                            self.blocked = False
                            return True
                        else:
                            iteration_number = iteration_number + 1
            else:
                occupancies = [first_occupancy, second_occupancy, third_occupancy] #finds the buffer with the least component and adds the component to it
                target_buf = min(occupancies)
                for buffer in self.buffers:
                    if buffer.get_occupancy() == target_buf:
                        buffer.increment_buffer(clock)
                        self.blocked = False
                        
                        return True
        

        else: #inspector is responsible for 2 components (second inspector who is responsible for C1 and C2). There shall be only 2 buffers in this inspector list
            for buffer in self.buffers:
                if(buffer.get_buffer_type() == input_component):
                    if(buffer.get_occupancy()<2):
                        buffer.increment_buffer(clock)
                        self.blocked = False
                        return True
            self.blocked = True
            return False #the buffer for a particular component type is full. 

    def is_blocked(self):
        return self.blocked
   
    
    def block(self):
        self.blocked = True
    
    def unblock(self):
        self.blocked = False

    def get_ID(self):
        return self.id