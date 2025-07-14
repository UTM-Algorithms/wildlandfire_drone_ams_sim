# request_processor.py
#
#  Module: Queue of requests
#  Module: data request. Queue of crews (each have queue request)
import math
import queue
import random
import sys

#####################################################################
#  Module for holding queue of requests. Generates requests from 
#  probability distribution.
class CrewRequest:
    '''
    Simple containter for holding mission requests:
        Generates desired mission path from random.
        Holds list (as queue) of requests
    '''
    LOW_PRIORITY = 3
    MID_PRIORITY = 2
    HIG_PRIORITY = 1

    def drawExpDist(self, scale):
        u = self.rand.uniform(0,1)
        x = float( -(1/scale) * math.log( (1-u) ))
        return x

    def drawUniDist(self, scale):
        x = scale * self.rand.uniform(0,1)
        return x

    def drawConstDist(self, scale):
        x = scale
        return x

    '''
    Specific crew methods
    '''

    def __init__(self, igeofence: int, ilrz: int, max_size=10, seed=12345):
        self.igeofence = igeofence
        self.ilrz = ilrz
        self.pqueue_requests = queue.PriorityQueue(max_size) #input=(priority_number "lowest first", data)
        self.curr_size = 0
        #---
        self.seed = seed
        self.rand = random.Random(seed)

    def __str__(self):
        txt = ""
        tmp_queue = queue.PriorityQueue(self.pqueue_requests.maxsize)
        while(0 < self.pqueue_requests.qsize()):
            peak = self.pqueue_requests.get()
            txt += str(peak) + f" pop size:{self.pqueue_requests.qsize()} - "
            tmp_queue.put(peak)
        while(0 < tmp_queue.qsize()):
            peak = tmp_queue.get()
            self.pqueue_requests.put(peak)
        return txt
    
    def addRequest(self, priority=-1, st_ige=-1, st_lrz=-1):
        if(-1==priority):
            priority = self.rand.choice( (CrewRequest.LOW_PRIORITY,CrewRequest.MID_PRIORITY,CrewRequest.HIG_PRIORITY) )
        if(-1==st_ige):
            st_ige = self.igeofence
        if(-1==st_lrz):
            st_lrz = self.ilrz
        data = (st_ige,st_lrz)
        self.pqueue_requests.put( (priority,data) )
    
    def processRequest(self):
        return self.pqueue_requests.get()

#####################################################################
#  Module for holding queue of crew requests. 
#  - process all crews per list per timestep
#  - no concurrency or parallelism (TODO: though could be implemented)
class DataCrewRequest:
    from mission_processor import DroneMissionPlanner
    '''
    Datastructure for holding all crew requests (and locations):
        Event-driven only need to update crew per situation.

    TODO: doesn't handle crew movement between LRZs.
    '''

    def __init__(self, missions: DroneMissionPlanner, max_size=10):
        self.list_crews = []
        self.max_crew_size = max_size 
        if(not missions.loadedData):
            print("ERROR: DataCrewRequest init() missions not loaded!")
            sys.exit(1)
        else:
            #missions loaded, so know all locations...
            flag_loop=False
            igeocnt=0
            for igeofence in missions.Loc_LRZ:
                for ilrz in igeofence: #item=(id,x,y)
                    igeocnt += 1
                    crew = CrewRequest(igeocnt,ilrz[0])
                    crew.addRequest()
                    self.list_crews.append(crew)
                    if(self.max_crew_size == len(self.list_crews)):
                        flag_loop = True
                        break
                if(flag_loop): 
                    break
            #end, assigned one mission per crew

    def __str__(self):
        txt = ""
        for icrew in self.list_crews:
            txt += str(icrew) +"\n"
        return txt

    '''Processes'''
    def addRequest(self, icrew: int, priority=-1, st_geofence=-1, st_lrz=-1):
        self.list_crews[icrew].addRequest(priority,st_geofence,st_lrz)

    def processRequest(self, icrew: int):
        return self.list_crews[icrew].closeRequest()
    
#####################################################################
# TESTING MODULE
#################
if __name__ == "__main__":
    print("START TEST request_processor.py")
    #  Requires mission_processor to finish/load graph
    import mission_processor as mp
    #---
    file = "../graphgenerator/path_output/log.txt"
    datamissions = mp.DataDroneMissionPlanner(file)
    missions = datamissions.missions
    crew_requests = DataCrewRequest(missions)
    print("Init():\n" + str(crew_requests))
    crew_requests.addRequest(0)
    print("1st Add[0]:\n" + str(crew_requests))
    crew_requests.addRequest(0)
    crew_requests.addRequest(2)
    print("2nd Add[0] and 1st Add[2]:\n" + str(crew_requests))
    #---
    print("END TEST request_processor.py")