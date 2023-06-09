"""
The Simulation class will manage the arrival and departure of components and consist of inspectors and workstations. 
The main method will use a loop to continuously call the Simulation classes that schedule the arrival and the departure 
as long as certain conditions are met. 

In this version of the simulation, time for inspection, buffer, and workstation assembling will not be taken into consideration
as it will be implemented in the next versions of the simulation submitted along with the next deliverable (second deliverable)

Authors
Peter Tanyous 101127203
Sara Shikhhassan 101142208
Sam Al Zoubi 101140949

Version 1 February 10, 2023

"""
from Component import Component
from Buffer import Buffer
from Inspector import Inspector
from Workstation import Workstation
import numpy as np
import math
import pandas as pd
import random

class Simulation:

    # m = 512
    # seed = 50
    # a = 13
    # c = 9 
    

    """
    Constructor
    """
    def __init__(self):
        #the simulation has three C1 buffers for workstations 1,2, and 3 
        self.buffer_C1_WST1 = Buffer(Component.C1, 1) #C1 buffer for workstation 1 
        self.buffer_C1_WST2 = Buffer(Component.C1, 2) #C1 buffer for workstation 2 
        self.buffer_C1_WST3 = Buffer(Component.C1, 3) #C1 buffer for workstation 3 
        #the simulation has one C2 buffer for workstation 2
        self.buffer_C2_WST2 = Buffer(Component.C2, 2) #C2 buffer for workstation 2 
        #the simulation has one C3 buffer for workstation 3
        self.buffer_C3_WST3 = Buffer(Component.C3, 3) #C3 buffer for workstation 3
        #the simulation has 3 workstations 
        self.workstation_one = Workstation(1, [self.buffer_C1_WST1])
        self.workstation_two = Workstation(2, [self.buffer_C1_WST2, self.buffer_C2_WST2])
        self.workstation_three = Workstation(3, [self.buffer_C1_WST3, self.buffer_C3_WST3])

        #the simulation has two inspectors 
        self.first_inspector = Inspector(1,[self.buffer_C1_WST1, self.buffer_C1_WST2, self.buffer_C1_WST3], [Component.C1] )
        self.second_inspector = Inspector(2, [self.buffer_C2_WST2, self.buffer_C3_WST3], [Component.C2 , Component.C3] )

        self.FEL = []
        self.clock = 0

    def print_elements_status(self):
        print("***************** Simulation Model Status *****************")
        print("                                            ")
        print("Clock time in seconds is " + str(self.clock))
        print("Inspector 1 status: " + str(self.first_inspector.get_status()))
        print("Inspector 2 status: " + str(self.second_inspector.get_status()))
        print("                                            ")
        print("buffer C1 for workstation 1 has " + str(self.buffer_C1_WST1.get_occupancy()) + " C1 components")
        print("buffer C1 for workstation 2 has " + str(self.buffer_C1_WST2.get_occupancy()) + " C1 components")
        print("buffer C1 for workstation 3 has " + str(self.buffer_C1_WST3.get_occupancy()) + " C1 components")
        print("buffer C2 for workstation 2 has " + str(self.buffer_C2_WST2.get_occupancy()) + " C2 components")
        print("buffer C3 for workstation 3 has " + str(self.buffer_C3_WST3.get_occupancy()) + " C3 components")
        print("                                            ")
        print(f"Workstation 1 status: {self.workstation_one.get_status()}")
        print(f"Workstation 2 is status: {self.workstation_two.get_status()} ")
        print(f"Workstation 3 is status: {self.workstation_three.get_status()}")
        print("      ")
        print("number of product P1 made: " + str(self.workstation_one.get_products_count()))
        print("number of product P2 made: " + str(self.workstation_two.get_products_count()))
        print("number of product P3 made: " + str(self.workstation_three.get_products_count()))
        
        
        print("***********************************************************")
        print("               ")

    """
    lcg_generate function takes four arguments: seed, a, c, and m
    seed is the chosen starting or current value in the sequence
    a, c, and m are the constants that determine the properties of the lcg
    generator. This function/generator calculates the next random number in 
    the sequence and returns it
    """
    def lcg_generate(self,seed, a, c, m):
        return (a * seed + c)% m
   
    """
    generate_LCG_random_numbers takes five arguments: seed, a, c, m, and n 
    seed is the chosen starting value or current value in the sequence
    a, c, and m are the constants that determine the properties of the lcg generator
    n is the numnber of random numbers to generate
    The function generates the n random numbers and returns them in an array
    """
    def generate_LCG_random_numbers(self,seed, a, c, m, n):
        rand_variates = []
        for i in range(n):
            seed = self.lcg_generate(seed, a, c, m)
            rand_variates.append(seed)
        rand_variates = [i / m for i in rand_variates]
        return rand_variates

    """
        Perform an autocorrelation test on a sequence of numbers. 
        parameters: values = sequence of numbers
                    lag = lag value
                    M = M value
                    i = starting index

        prints out p value, standard deviation of the estimator, and the calculated z value
    """
    def autocorrelation_test(self,values, lag, M, i):
        
        sum_products = 0
        for k in range(M):
            index1 = i + (k * lag)
            index2 = i + ((k + 1) * lag)
            sum_products += values[index1] * values[index2]

        p = 1 / (M + 1) * sum_products - 0.25
        standard_dev = (13 * M + 7) ** 0.5 / (12 * (M + 1))
        z = p / standard_dev

        print(f"p = "+ str(p))
        print(f"standard deviation of the estimator = " +str(standard_dev))
        print(f"z = "+ str(z))


    """
        performs kolmogorov_smirnov uniformity test on sequence of random numbers
        parameter: data is the input array of random variates
        returns the value of d by finding the maximum value between d_plus and d_minus
    """
    def kolmogorov_smirnov_uniform_test(self, data):
        sorted_data = sorted(data)
        i_divided_N = [(i + 1) / len(data) for i in range(len(data))]
        i_divided_N_minus_Ri = []
        for i in range(len(sorted_data)):
            i_divided_N_minus_Ri.append(i_divided_N[i] - sorted_data[i])
        i_minus_one_divided_by_n = [i / 300 for i in range(300)]
        Ri_minus_i_minus_one_divided_by_n = []
        for i in range(len(sorted_data)):
            Ri_minus_i_minus_one_divided_by_n.append(sorted_data[i] - i_minus_one_divided_by_n[i])
        d_plus = max(i_divided_N_minus_Ri)
        d_minus = max(Ri_minus_i_minus_one_divided_by_n)
        d = max(d_plus, d_minus)
        return d 

    """
        generates the exponential of the input value using the input lambda
        paramter: 
    """
    def get_exponential_value(self,value, lam_bda):
        # check if lam_bda is positive
        if lam_bda <= 0:
            print("Error: lambda must be positive.")
            return 0
        # compute the exponential value
        return (-math.log(1 - value)) / lam_bda

    def compute_exponential_array(self, data, lam_bda):
        result =[]
        for x in data:
            result.append(self.get_exponential_value(x,lam_bda))
        return result
    """
    This function is used to generate arrival times for the computed service times in milestone 3 to run the simulation
    """
    def generate_arrival_times(self, service_times):
        # Estimate the arrival rate
        arrival_rate = 1 / np.mean(service_times)
        # Calculate the interarrival times
        interarrival_times = np.random.exponential(scale=1/arrival_rate, size=len(service_times))
        # Set the first arrival time to 0
        arrival_times = [0]
        # Generate the arrival times for the remaining customers
        for i in range(1, len(service_times)):
            arrival_times.append(arrival_times[i-1] + interarrival_times[i-1])
        return arrival_times
    """
    This function creates events to be added to FEL
    """
    def create_event(self, e_type, object_type, event_time):
        new_tuple = (e_type, object_type, event_time)
        return new_tuple
    
    """
    This function is used to add event notices to FEL
    """
    def add_event_notice_to_FEL(self, event_notice):
        self.FEL.append(event_notice)
        self.FEL.sort(key = lambda x: x[2])

    def generate_random_2_or_3(self):
        return random.randint(2, 3)

    def Average(self, lst):
        return sum(lst) / len(lst)

    def calculate_throughput(self, seconds, num_products):
        throughput_per_sec = num_products / seconds
        return throughput_per_sec

    def run(self):
        """
        This part is only for initialization
        """
        # m = 512, seed = 50, a = 13, c = 9 
        #generate_LCG_random_numbers(seed, a, c, m, n)
        print(f"generating LCG random numbers")
        print(f"seed value = 50, a = 13, c = 9, m = 512")
        print(f"number of values = 300")
        z = self.generate_LCG_random_numbers(50, 13,  9, 512, 300)
        print(f"----------------Separator----------------")
        print(f"performing kolmogorov smirnov uniformity test on generated data")
        D = self.kolmogorov_smirnov_uniform_test(z)
        print(f"computed D value = " + str(D))
        print(f"----------------Separator----------------")
        print(f"performing autocorrelation test")
        print(f"lag value = 4, M = 73, i = 1 ")
        self.autocorrelation_test(z, 4, 73, 1)
        print(f"----------------Separator----------------")
        #inspector 1 lambda = 0.09654457318, inspector 2 component 2 lambda = 0.06436289, inspector 2 component 3 lambda = 0.04846662111
        #workstation 1 lambda = 0.21718277739, workstation 2 lambda =  0.090150136, workstation 3 lambda =  0.11369346876
        inspector_one_service_times = self.compute_exponential_array(z, 0.09654457318)
        inspector_two_service_times_component_2 = self.compute_exponential_array(z, 0.06436289)
        inspector_two_service_times_component_3 = self.compute_exponential_array(z, 0.04846662111)
        workstation_one_service_times = self.compute_exponential_array(z, 0.21718277739)
        workstation_two_service_times = self.compute_exponential_array(z, 0.090150136)
        workstation_three_service_times = self.compute_exponential_array(z, 0.11369346876)
        print(f"All service times for inspectors 1, 2, 3, and workstations 1, 2, 3 have been generated")
        print(f"Initializing clock to 0, the clock times here is only counting seconds")
        print(f"                                       ")
        print(f"                                       ")
        print(f" STARTING SIMULATION ")

        blocked_inspectors = [] #The array that holds the blocked inspectors to create arrival events
        #for when buffers are emptied
        blocked_workstations = [] #The array that holds the blocked workstations to create arrival events
        #for them when new components are added to buffer. 
        simulation_stopper = 3000  #A simulation stopper variable used in while loop to track iterations
        
        self.second_inspector.set_next_component_to_make(Component.C3) 

        #Initializing first Arrival events to be used on start of the while loop (simulation)
        self.add_event_notice_to_FEL(self.create_event("arrival",  self.first_inspector, 0))
        self.add_event_notice_to_FEL(self.create_event("arrival", self.second_inspector,  0))
        self.add_event_notice_to_FEL(self.create_event("arrival", self.workstation_one, 0))
        self.add_event_notice_to_FEL(self.create_event("arrival", self.workstation_two, 0))
        self.add_event_notice_to_FEL(self.create_event("arrival", self.workstation_three, 0))
        counter = 0 #to count iterations numbers, was used in testing only. 

        """
        The variables declared below until the while loop are used to calculate the heuristics
        required to reflect on the simulation
        """
        inspector_one_blocked_time_start = None #Holds the start time of which the first inpector is blocked
        #^ This value is used and re-initialized in while loop as inspector 1 gets blocked or unblocked
        #and is used to calulate the total block time of inspector 1 through the simulation 

        inspector_one_blocked_time_total = 0 #Tracks the sum of total block time for inspector 1 in simulation
        
        #Same is done for inspector 2. 
        inspector_two_blocked_time_start = None
        inspector_two_blocked_time_total = 0

        #These variables are used to calculate the sum of the working stations working times in the simulation
        #done for all 3 workstations to compute later idle time for each workstation (required in heuristics)
        total_time_workstation_1_working = 0
        total_time_workstation_2_working = 0 
        total_time_workstation_3_working = 0 

        #These variables are used to find each buffer's occupancy in each CLOCK Change and adds them to 
        #the arrays of occupancies below. This is used to calculate average buffer occupancies heuristics
        #Note C1WS1 means Component 1 of Workstation 1 
        last_clock = None
        last_clock_buffer_occupancy_C1WS1 = 0
        last_clock_buffer_occupancy_C1WS2 = 0
        last_clock_buffer_occupancy_C1WS3 = 0
        last_clock_buffer_occupancy_C2WS2 = 0
        last_clock_buffer_occupancy_C3WS3 = 0


        occupancies_C1WS1 = []
        occupancies_C1WS2 = []
        occupancies_C1WS3 = []
        occupancies_C2WS2 = []
        occupancies_C3WS3 = []

        while simulation_stopper > 0:
            counter = counter + 1 
            first_element = self.FEL.pop(0)
            self.clock = first_element[2]
                
            if first_element[0] == "arrival":
                if isinstance(first_element[1], Inspector): #checks if the arrival event is for an inspector
                    if first_element[1].get_ID() == 1: #checks if it is inspector 1 
                        completion_time = self.clock + inspector_one_service_times.pop(0) #get inspector 1 service time
                    elif first_element[1].get_ID() == 2:#checks else if it is inpector 2 
                        if first_element[1].get_next_component_to_make() == Component.C2: #if it is making component C2
                            completion_time = self.clock + inspector_two_service_times_component_2.pop(0) #Get Inspector2 C2 service time
                        elif first_element[1].get_next_component_to_make() == Component.C3:#if it is making component C3
                            completion_time = self.clock + inspector_two_service_times_component_3.pop(0)# Get Inspector2 C3 service time
                    new_event = self.create_event("completion", first_element[1], completion_time ) #creates the completion event accordingly 
                    self.add_event_notice_to_FEL(new_event) #adds the scheduled completion event to FEL
                    first_element[1].set_busy(True) #makes inspector busy until the completion event is reached
                    first_element[1].update_inspector_status() #updates the inspector status
                else: #else it is a workstation arrival event
                    if first_element[1].make_product(self.clock):# checks if workstation is able to make product
                        if first_element[1].get_ID() == 1: #if it is the first workstation
                            w_1_st = workstation_one_service_times.pop(0) #get workstation 1 service time to compute completion time
                            completion_time = self.clock + w_1_st #compute future completion time
                            total_time_workstation_1_working = total_time_workstation_1_working + w_1_st #update total work time for workstation
                        elif first_element[1].get_ID() == 2: #if it is the second workstation
                            w_2_st = workstation_two_service_times.pop(0) #get workstation 2 service time to compute completion time
                            completion_time = self.clock + w_2_st  #compute future completion time
                            total_time_workstation_2_working = total_time_workstation_2_working + w_2_st#update total work time for workstation
                        elif first_element[1].get_ID() == 3:#if it is the third workstation
                            w_3_st = workstation_three_service_times.pop(0)#get workstation 3 service time to compute completion time
                            completion_time = self.clock + w_3_st #compute future completion time
                            total_time_workstation_3_working = total_time_workstation_3_working + w_3_st#update total work time for workstation
                        new_event = self.create_event("completion", first_element[1], completion_time )#create the completion event accordingly
                        first_element[1].set_busy(True) #make workstation busy
                        first_element[1].update_workstation_status() #update workstation status
                        self.add_event_notice_to_FEL(new_event) #add the completion event to the FEL
                        for f in blocked_inspectors: #now that workstation used the components in buffers
                            new_f = (f[0], f[1], self.clock) #free the blocked inspectors to add their components to the buffer
                            self.add_event_notice_to_FEL(new_f) #add the blocked inspectors events to FEL
                        blocked_inspectors = [] #re- initialize blocked_inpectors to be empty
                    else: #if the workstation cannot make the product (components are not available)
                        first_element[1].update_workstation_status() #update the workstation status
                        blocked_workstations.append(first_element) #add the workstation to blocked_workstation list
            elif first_element[0] == "completion": #else if the event is a completion event
                if isinstance(first_element[1], Inspector): #it checks if the event is from an inspector
                    if first_element[1].get_ID() == 1: # If it is the first inspector 
                        addition_component = Component.C1 #The component to be inspected by the inspector is component 1
                        first_element[1].set_next_component_to_make(addition_component) #inspector is set to know the component to inspect
                    else: #else if it is the second inspector 
                        x = self.generate_random_2_or_3() #The code generate a random number 2 or 3 (to decide on the component Inspector shall inspect)
                        if x == 2:  #if the random number is 2
                            addition_component = Component.C2 # the additional component to inspect is C2
                            first_element[1].set_next_component_to_make(addition_component) #the inspector is set know the component to inspect
                        elif x == 3: #if the random number is 3
                            addition_component = Component.C3 #the additional component to inspect is C3
                            first_element[1].set_next_component_to_make(addition_component) #the inspector is set know the component to inspect
                    if first_element[1].send_target_buffer(addition_component, self.clock): #then the inspector checks if it can send the component to the target buffer (As per the send_target_buffer implemented algorithm that has the priorities defined )
                        if first_element[1].get_ID() == 1: # if inspector 1 sent it to the buffer
                            if inspector_one_blocked_time_start == None: #checks if it wasnt been blocked at a certain time
                                pass
                            else: #if it was blocked at a time 
                                inspector_one_blocked_time_total = inspector_one_blocked_time_total +  (self.clock - inspector_one_blocked_time_start) # the blocked time total is calculated for the heuristics
                                inspector_one_blocked_time_start = None #and now there is no bloked time as it is not blocked
                        else: #second inspector 
                            if inspector_two_blocked_time_start == None: #checks if it wasnt blocked at a certain time
                                pass
                            else:# if it was blocked 
                                inspector_two_blocked_time_total = inspector_two_blocked_time_total + (self.clock - inspector_two_blocked_time_start) # the blocked time total is calculated for the heuristics
                                inspector_two_blocked_time_start = None#and now there is no blocked time as it is not blocked 

                        self.add_event_notice_to_FEL(self.create_event("arrival", first_element[1] , self.clock)) #adds a new event notice to have the inspector start inspecting a new component after sending to the buffer
                        first_element[1].set_status("Sent Component to Buffer") #updates the status of the inspector
                        for f in blocked_workstations: #if there are blocked workstation
                            new_f = (f[0], f[1], self.clock) # these workstations are now free since new components have been added to buffers
                            self.add_event_notice_to_FEL(new_f) #arrival events with current time clock are sent to FEL
                        blocked_workstations = [] #no more blocked workstations
                    else: #if inspector is blocked and cannot send to the target buffer (because it is full)
                        blocked_inspectors.append(first_element) #the inspector completion event is blocked and is added to the blocked_inspectors list
                        if first_element[1].get_ID() == 1: #if it is the first inspector
                            inspector_one_blocked_time_start = self.clock #the blocked time start of it is re-initialized with the current clock time
                        elif first_element[1].get_ID() == 2: #else if it is the second inspector
                            inspector_two_blocked_time_start = self.clock # the blocked time start of it is re-initialized with the current clock time
                else: #a workstation instance 
                    first_element[1].increment_product_count() #the workstation increments the product count 
                    first_element[1].set_status("Product Created") #updates its status
                    new_event = self.create_event("arrival", first_element[1], self.clock ) #creates a new arrival event for the workstation with the current clock time
                    self.add_event_notice_to_FEL(new_event) #adds the arrival event to FEL
            
            simulation_stopper = simulation_stopper - 1 #simulation stopper is decremented to makesure that the simulation stops at some point
            if self.clock != last_clock: #the clock has changed since the last iteration (not events arriving at the same time)
                occupancies_C1WS1.append(last_clock_buffer_occupancy_C1WS1) #update Component 1 Buffer of workstation 1 occupancies list by adding the buffer occupancy of the lat clock iteration. This is used to later calculate the average buffer occupancy on clock change
                occupancies_C1WS2.append(last_clock_buffer_occupancy_C1WS2) #update Component 1 Buffer of workstation 2 occupancies list by adding the buffer occupancy of the lat clock iteration. This is used to later calculate the average buffer occupancy on clock change
                occupancies_C1WS3.append(last_clock_buffer_occupancy_C1WS3)#update Component 1 Buffer of workstation 3 occupancies list by adding the buffer occupancy of the lat clock iteration. This is used to later calculate the average buffer occupancy on clock change
                occupancies_C2WS2.append(last_clock_buffer_occupancy_C2WS2)#update Component 2 Buffer of workstation 2 occupancies list by adding the buffer occupancy of the lat clock iteration. This is used to later calculate the average buffer occupancy on clock change
                occupancies_C3WS3.append(last_clock_buffer_occupancy_C3WS3)#update Component 3 Buffer of workstation 3 occupancies list by adding the buffer occupancy of the lat clock iteration. This is used to later calculate the average buffer occupancy on clock change
                last_clock = self.clock #re-initialize last_clock 
            else: #if the clock didnot change 
                last_clock_buffer_occupancy_C1WS1 = self.buffer_C1_WST1.get_occupancy()#update Component 1 Buffer of workstation 1 occupancy in this clock iteration
                last_clock_buffer_occupancy_C1WS2 = self.buffer_C1_WST2.get_occupancy()#update Component 1 Buffer of workstation 2 occupancy in this clock iteration
                last_clock_buffer_occupancy_C1WS3 = self.buffer_C1_WST3.get_occupancy()#update Component 1 Buffer of workstation 3 occupancy in this clock iteration
                last_clock_buffer_occupancy_C2WS2 = self.buffer_C2_WST2.get_occupancy()#update Component 2 Buffer of workstation 2 occupancy in this clock iteration
                last_clock_buffer_occupancy_C3WS3 = self.buffer_C3_WST3.get_occupancy()#update Component 3 Buffer of workstation 3 occupancy in this clock iteration

            #print out the element status to view the status of each element in the manufacturing plant on each iteration
            self.print_elements_status()
            
            #if the products produced add up to 299, This means that 300 Component 1 have been used and this means that we ran out of service times for inpector 1 for component 1
            #because we only had 300 service times calculated for all inspectors and workstations in the previous milestone
            if (self.workstation_one.get_products_count() + self.workstation_two.get_products_count() + self.workstation_three.get_products_count()) == 299:
                #ends the simulation
                print(f"END OF SIMULATION")
                print(f"No more service times are available for Inspector 1 to inspect C1")
                print(f"                                     ")
                print(f"PRINTING REQUIRED HEURISTICS")
                simulation_stopper = 0

            
        #This is run after the simulation has reached to an end to show the 12 heuristics required for milestone 3
        throughput_P1 = self.calculate_throughput(self.clock, self.workstation_one.get_products_count()) #calculate the throughput given the number of products 1 created and time they took in seconds (clock)
        throughput_P2 = self.calculate_throughput(self.clock, self.workstation_two.get_products_count())#calculate the throughput given the number of products 2 created and time they took in seconds (clock)
        throughput_P3 = self.calculate_throughput(self.clock, self.workstation_three.get_products_count())#calculate the throughput given the number of products 3 created and time they took in seconds (clock)
        throughput_P1_per_hour = throughput_P1 * 3600 #converts throughput per second to throughput per hour for product 1
        throughput_P2_per_hour = throughput_P2 * 3600 #converts throughput per second to throughput per hour for product 2
        throughput_P3_per_hour = throughput_P3 * 3600  #converts throughput per second to throughput per hour for product 3
        print(f"clock end time is {self.clock}") # prints the clock end time 
        print(f"Number of products P1 made is {self.workstation_one.get_products_count()}") #prints the number of products P1 made
        print(f"Number of products P2 made is {self.workstation_two.get_products_count()}") #prints the number of products P2 made
        print(f"Number of products P3 made is {self.workstation_three.get_products_count()}")#prints the number of products P2 made
        print(f"The throughput per hour for Product 1 is {throughput_P1_per_hour}") #prints the calculated throughput per hour for P1
        print(f"The throughput per hour for Product 2 is {throughput_P2_per_hour}")#prints the calculated throughput per hour for P2
        print(f"The throughput per hour for Product 3 is {throughput_P3_per_hour}")#prints the calculated throughput per hour for P3
        print(f"Total blocked time for Inspector 1 in seconds is {inspector_one_blocked_time_total}") #prints the total blocked time for inspector 1 that was calculated throughout the simulation 
        print(f"Total blocked time for Inspector 2 in seconds is {inspector_two_blocked_time_total}")#prints the total blocked time for inspector 2 that was calculated throughout the simulation 
        print(f"Total idle time for workstation 1 in seconds is {self.clock - total_time_workstation_1_working}") #prints the total idle time for workstation 1 after substracting the total time of workstation working from the  current clock time 
        print(f"Total idle time for workstation 2 in seconds is {self.clock - total_time_workstation_2_working}")#prints the total idle time for workstation 2 after substracting the total time of workstation working from the  current clock time 
        print(f"Total idle time for workstation 3 in seconds is {self.clock - total_time_workstation_3_working}")#prints the total idle time for workstation 3 after substracting the total time of workstation working from the  current clock time 
        print(f"Average buffer occupancy for buffer C1 of workstation 1 is {self.Average(occupancies_C1WS1)}") # prints and finds the average buffer C1 occupancy for workstation 1 by finding the average of the occupancies list that has the buffer occupancy at each iteration in the simulation
        print(f"Average buffer occupancy for buffer C1 of workstation 2 is {self.Average(occupancies_C1WS2)}")# prints and finds the average buffer C1 occupancy for workstation 2 by finding the average of the occupancies list that has the buffer occupancy at each iteration in the simulation
        print(f"Average buffer occupancy for buffer C1 of workstation 3 is {self.Average(occupancies_C1WS3)}")# prints and finds the average buffer C1 occupancy for workstation 3 by finding the average of the occupancies list that has the buffer occupancy at each iteration in the simulation
        print(f"Average buffer occupancy for buffer C2 of workstation 2 is {self.Average(occupancies_C2WS2)}")# prints and finds the average buffer C2 occupancy for workstation 2 by finding the average of the occupancies list that has the buffer occupancy at each iteration in the simulation
        print(f"Average buffer occupancy for buffer C3 of workstation 3 is {self.Average(occupancies_C3WS3)}")# prints and finds the average buffer C3 occupancy for workstation 3 by finding the average of the occupancies list that has the buffer occupancy at each iteration in the simulation
        print(f"Average time component C1 spends in buffer C1 of workstation 1 is {self.Average(self.buffer_C1_WST1.get_times_spent_in_buffer())}") #each buffer has a list of the times each component spends in the buffer, its implementation can be found in the buffer Class
        print(f"Average time component C1 spends in buffer C1 of workstation 2 is {self.Average(self.buffer_C1_WST2.get_times_spent_in_buffer())}") #prints the average time spent by the components in each buffer
        print(f"Average time component C1 spends in buffer C1 of workstation 3 is {self.Average(self.buffer_C1_WST3.get_times_spent_in_buffer())}")
        print(f"Average time component C2 spends in buffer C2 of workstation 2 is {self.Average(self.buffer_C2_WST2.get_times_spent_in_buffer())}")
        print(f"Average time component C3 spends in buffer C3 of Workstation 3 is {self.Average(self.buffer_C3_WST3.get_times_spent_in_buffer())} ")

def main():
    simulate = Simulation()
    simulate.run()


if __name__ == "__main__":
    main()