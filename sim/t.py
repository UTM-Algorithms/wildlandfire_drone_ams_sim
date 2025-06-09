# data_queue.py
#
#  Module for storing and retrieving customer inquires.
#  Also used for available drones.
import queue
import drone

#####################################################################
class DataDepot:
    '''Datastucture for storing customer inquires at depots'''
    
    def __init__(self, type="FCFS" ,max_customer_size=0):
        if(type=="FCFS"):
            self.customer_queue = queue.Queue(max_customer_size) #input=(data)
        elif(type=="Priority"):
            self.customer_queue = queue.PriorityQueue(max_customer_size) #input=(priority_number "lowest first", data)
        else:
            print("DataDepot Init: "+type)
        self.max_customer_size = max_customer_size
        self.type = type
        self.nextCustomerId = None

    '''Methods for managing customers'''
    def addCustomerId(self, id):
        status = False
        if(self.max_customer_size==0 or (self.max_customer_size > self.getCurrCustomerSize())):
            self.customer_queue.put(id) #enqueue
            status = True
        #end check
        return status
    
    def getNextCustomerId(self):
        if( self.nextCustomerId == None ):
            self.nextCustomerId = self.customer_queue.get() #dequeue
        return self.nextCustomerId
    
    def getCurrCustomerSize(self):
        return self.customer_queue.qsize()
    
    def clearNextCustomerId(self):
        self.nextCustomerId = None

#####################################################################
class DataBuffer:
    '''Datastructure for storing drones at crossing'''

    def __init__(self, type="FCFS" ,max_drone_size=0):
        if(type=="FCFS"):
            self.drone_queue = queue.Queue(max_drone_size) #input=(data)
        elif(type=="Priority"):
            self.drone_queue = queue.PriorityQueue(max_drone_size) #input=(priority_number "lowest first", data)
        else:
            print("DataBuffer Init: "+type)
        self.max_drone_size = max_drone_size
        self.type = type
        self.nextDroneId = None

    '''Methods for managing stopped airborne drones'''
    def addDroneId(self, id):
        status = False
        if(self.max_drone_size==0 or (self.max_drone_size > self.getCurrDroneSize())):
            self.drone_queue.put(id) #enqueue
            status = True
        #end check
        return status
    
    def getNextDroneId(self):
        if( self.nextDroneId == None and 0<self.getCurrDroneSize() ):
            self.nextDroneId = self.drone_queue.get() #dequeue
        return self.nextDroneId
    
    def getCurrDroneSize(self):
        return self.drone_queue.qsize()
    
    def getList(self):
        return list(self.drone_queue.queue)
    
    def clearNextDroneId(self):
        ret = self.nextDroneId 
        self.nextDroneId = None
        return ret


#####################################################################
# TESTING MODULE
#################
if __name__ == "__main__":
    #  Uses mathplotlib. `python -m pip install -U matplotlib`
    import matplotlib.pyplot as plt             #main plotting
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = 'Times New Roman'
    fig, ax = plt.subplots()
    #  Uses drone module for vehicle models
    import drone as ua
    #  Uses customer_time / create_data for input data
    import customer_time as ct
    #
    import math #for 'math'
    import sys, os #for error handling stuff

    #--- setup graph / mission planner
    graphFile = "sim_input/_test/graph_matrix.csv"
    testGraph = ua.DroneMissionPlanner()
    assert( testGraph.loadGraph(graphFile) )
    #
    pathsFile = "sim_input/_test/paths_s.txt"
    assert( testGraph.loadPaths(pathsFile) )
    #
    depotLocFile = "sim_input/_test/depot_loc.txt"
    assert( testGraph.loadDepots(depotLocFile) )
    custLocFile = "sim_input/_test/customer_loc.txt"
    assert( testGraph.loadCustomers(custLocFile) )
    #--- end setup graph / mission planner

    #--- setup locations
    # Depot locations data
    xdata_dept_list = []
    ydata_dept_list = []
    for idata in testGraph.Dept_Loc:
        xdata_dept_list.append( idata[1] )
        ydata_dept_list.append( idata[2] )
    # Customer locations data
    xdata_cust_list = []
    ydata_cust_list = []
    for idata in testGraph.Cust_Loc:
        xdata_cust_list.append( idata[1] )
        ydata_cust_list.append( idata[2] )
    # Buffer locations data
    xdata_buff_list = []
    ydata_buff_list = []
    for idata in testGraph.Cros_Loc:
        xdata_buff_list.append( idata[0] )
        ydata_buff_list.append( idata[1] )
    #--- end setup locations

    #--- setup customer data input
    poisson_client_arr_rate = 100 #orders/hour
    scale = poisson_client_arr_rate / (60*60) #convert to (orders/sec) for use in sim
    cust = ct.CustomerSimTime(scale, testGraph.num_cust,testGraph.num_dept, seed=12345)
    #--- end setup customer data input

    #---
    speed = 20  #m/s
    setup = 10 #sec
    Ts = 5 #sec (time step)
    size = 1 #meters
    h = 150 #plot values
    #---
    cust_list = []
    for idept in range(testGraph.num_dept):   #TODO: currently assume each depot has same input process
        depot_input_model = "FCFS"
        cust_list.insert(idept, DataDepot(depot_input_model))
        print("Depot customer ,%d,%s" %(idept,depot_input_model))
    dron_list = []
    for idept in range(testGraph.num_dept):   #TODO: currently assume each depot has same number of drones
        drones_per_depot = 100
        dron_list.insert(idept, DataDrone(drones_per_depot))
        print("Depot drone ,%d,%d" %(idept,drones_per_depot))
    cros_list = []
    for icros in range(testGraph.num_wayt):
        buffer_input_model = "FCFS"
        cros_list.insert(icros, DataBuffer(buffer_input_model))
        print("Crossing ,%d,%s" %(icros,buffer_input_model))
    #
    itime = 0
    it = 0
    #
    icustid = -1
    ideptid = -1
    #
    icnt = 0
    tot_dron_done_cnt = 0
    while(True):
        tot_fly_cnt = 0
        #init print
        plt.cla()
        plt.axis([-h,1000+h,-h,1000+h])
        # 2D top-view of simulation map
        plt.scatter(xdata_dept_list,ydata_dept_list, c='orange',s=80, edgecolors='none', label='depot')
        plt.scatter(xdata_cust_list,ydata_cust_list, c='blue',s=20, edgecolors='none', label='customer')
        plt.scatter(xdata_buff_list,ydata_buff_list, c='green',s=20, edgecolors='none', label='buffer')
        #end, init print

        try:
            if( it <= itime ):
                if(-1 < icustid and -1 < ideptid):
                    assert(cust_list[ideptid].addCustomerId(icustid))
                it = cust.getNextExpTime(itime)
                icustid = cust.getCustomerId()
                ideptid = cust.getDepotId()
                icnt = icnt + 1
                cust_size0 = cust_list[0].getCurrCustomerSize()
                cust_size1 = cust_list[1].getCurrCustomerSize()
                print("\nCUSTOMER CNT = "+str(icnt))
                print("   depot<"+str(cust_size0)+":"+str(list(cust_list[0].customer_queue.queue))+">")
                print("   depot<"+str(cust_size1)+":"+str(list(cust_list[1].customer_queue.queue))+">")
            #---

            for idept in range(testGraph.num_dept):
                #make sure there are customers
                cust_size = cust_list[idept].getCurrCustomerSize()
                #print("num customers = %d\n" %cust_size)
                if(0 < cust_size):
                    curr_cust_id = cust_list[idept].getNextCustomerId()
                    testroute = testGraph.generateRoute(idept,curr_cust_id,speed,setup)
                    x = testroute[0][0]
                    y = testroute[1][0]
                    #
                    assert(dron_list[idept].groundDroneAdd(testroute,curr_cust_id,size,speed,x,y))
                    cust_list[idept].clearNextCustomerId() #launched drone, so can clear request for next customer
                #check drones
                if( dron_list[idept].flyDroneRemoveAllDone() ): #remove method is loop
                    tot_dron_done_cnt += len( dron_list[idept].drones_list_fly_done_recent )
                for testdrone in dron_list[idept].drones_list_fly:
                    tot_fly_cnt += 1
                    x = testdrone.x
                    y = testdrone.y
                    #
                    #advance step for fly drone
                    #1. check if need to put into buffer
                    icnt=0
                    flag=False
                    #print(""+str(len(testGraph.Cros_Loc))+": "+str(testGraph.Cros_Loc))
                    for iwaypt in testGraph.Cros_Loc:
                        id = cros_list[icnt].getNextDroneId()
                        if(id==testdrone.id):
                            #already waiting here, free it
                            cros_list[icnt].clearNextDroneId()
                            break
                        else:
                            #not waiting here, should we add it?
                            ixw = float(iwaypt[0])
                            iyw = float(iwaypt[1])
                            ir = math.sqrt( math.pow(x-ixw,2.0)+math.pow(y-iyw,2.0) )
                            #check if not waiting and within range
                            if( ir<=50 and 0<testdrone.speed ):
                                flag = True
                                testdrone.pause(Ts)
                                cros_list[icnt].addDroneId(testdrone.id)
                                break
                        #
                        icnt += 1
                    #end
                    if(flag):
                        plt.scatter(x,y, c='red',s=20, edgecolors='none', label='wait UAV')
                    else:
                        plt.scatter(x,y, c='purple',s=20, edgecolors='none', label='UAV')
                    #end
                    #2. apply motion
                    (status,messageMove) = testdrone.moveTs(Ts)
                    assert(status)
                    (status,messageRoute) = testdrone.updateRouteStatus()
                    assert(status)
                    #print("T=%f MOVE>\t %s:%s" %(itime,messageMove,messageRoute))
                for testdrone in dron_list[idept].drones_list_ground:
                    #advance step for wait drone
                    (status,messageMove) = testdrone.moveTs(Ts)
                    assert(status)
                    (status,messageRoute) = testdrone.updateRouteStatus()
                    assert(status)
                    #print("T=%f WAIT>\t %s:%s" %(itime,messageMove,messageRoute))
                    if(testdrone.status == ua.Drone.GROUND_READY):
                        assert(dron_list[idept].groundDroneLaunch())
            #---

            #update time
            itime += Ts

        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            break

        #end, now print
        plt.text(400,1200, "Time= "+str(itime)+"/"+str(it)+" - Fly= "+str(tot_fly_cnt))
        plt.pause(1)
    #end
    cust.closeFile()

