# drone_processor.py
#
#  Module: drone
#  Module: data drone. Queue of drone
import traceback
import math
from scipy.integrate import solve_ivp   #for ode kinematics solving

#####################################################################
#  Module for storing drone information status.
class Drone:
    '''
    Drone status info:
        all distance is (meter)
        all time is (sec)
    '''
    DRONE_ID = 0                #next free drone's info id (auto inc)

    GROUND_NO_OPS = -1  #at lrz, no ops
    GROUND_WAIT = 0     #at lrz, assigned ops, waiting for deploy
    GROUND_READY = 1    #at lrz, assigned ops, ready to launch
    FLY_MOVE = 2        #flying mission
    FLY_WAIT = 3        #flying mission, temp pause

    def ode_fun(t, X):
        '''
        ode system solver for drone modeled as deterministic
        point-mass with constant heading and speed for t sec
            dx      = speed*cos(heading)dt
            dy      = speed*sin(heading)dt
            dheading= 0
            dspeed  = 0
        '''
        f = [   X[3]*math.cos(X[2]), 
                X[3]*math.sin(X[2]),
                0,
                0
            ]
        return f

    '''
    Specific drone methods:
    '''

    def __init__(self, drone_size, drone_speed, x,y):
        '''
        default init method:
            Creates drone with size and speed modeled as ode_fun.
            Gives a unique DRONE_ID (upto int numbers range).
        '''
        #service time
        self.time = 0
        #drone state
        self.state = Drone.GROUND_NO_OPS
        #drone characteristics
        self.size = drone_size
        self.speed = drone_speed
        self.pause_time = 0
        #pos id
        self.heading = 0
        self.x = x
        self.y = y
        #information id
        self.id = Drone.DRONE_ID
        Drone.DRONE_ID += 1

    def __str__(self):
        txt = "Drone<"+str(self.id)+"> State<"+self.getStrState()+">\n"
        txt += "\t-Pos<"+str(self.x)+","+str(self.y)+">\n"
        txt += "\t-Head<"+str(self.heading)+">\n"
        txt += "\t-Size<"+str(self.size)+">\n"
        txt += "\t-Speed<"+str(self.speed)+">\n"
        return(txt)

    def getStrState(self) -> str:
        txt = ""
        if(  Drone.GROUND_NO_OPS == self.state):
            txt = "GROUND_NO_OPS"
        elif(Drone.GROUND_WAIT == self.state):
            txt = "GROUND_WAIT"
        elif(Drone.GROUND_READY == self.state):
            txt = "GOUND_READY"
        elif(Drone.FLY_MOVE == self.state):
            txt = "FLY_MOVE"
        elif(Drone.FLY_WAIT == self.state):
            txt = "FLY_WAIT"
        return txt

    def pause(self, Ts):
        '''
        Temporary pause drone (set speed=0) for Ts seconds.
        Can be used for basic conflict resolution.
        '''
        status = False
        message = ""+str(self.id)
        if(Drone.FLY_MOVE==self.state):
            self.state = Drone.FLY_WAIT
            message += "- paused"
            status = True
        else:
            message += "- NOTE already waiting<"+str(self.state)+">"
        #end, now pause
        self.pause_time += Ts
        return (status,message)
    
    def assignMission(self):
        status = False
        message = ""+str(self.id)
        if(Drone.GROUND_NO_OPS==self.state):
            self.state = Drone.GROUND_WAIT
            message += "- assigned and wait"
            status = True
        else:
            message += "- ERROR assign<"+str(self.state)+">"
        #end
        return (status,message)

    def launch(self):
        status = False
        message = ""+str(self.id)
        if(Drone.GROUND_READY==self.state):
            self.state = Drone.FLY_MOVE
            message += "- launched"
            status = True
        else:
            message += "- ERROR launch<"+str(self.state)+">"
        #end
        return (status,message)
    
    def land(self):
        status = False
        message = ""+str(self.id)
        if(Drone.FLY_MOVE==self.state or Drone.FLY_WAIT==self.state):
            self.state = Drone.GROUND_WAIT
            message += "- landed"
            status = True
        else:
            message += "- ERROR land<"+str(self.state)+">"
        #end
        return (status,message)

    def moveTs(self, Ts: float):
        '''
        Drone moves in heading dir for Ts seconds
        '''
        status = False
        message = ""+str(self.id)
        try:
            #now update pause time
            if( 0 < self.pause_time ):
                self.pause_time -= Ts
            elif( Drone.FLY_WAIT==self.state ):
                self.state = Drone.FLY_MOVE
            #end, pause check
            #make sure it is in moving state
            if(Drone.FLY_MOVE==self.state):
                sol = solve_ivp(Drone.ode_fun, [0,Ts], [self.x,self.y,self.heading,self.speed])
                self.x = sol.y.T[-1, 0]
                self.y = sol.y.T[-1, 1]
                self.heading = sol.y.T[-1, 2]
                self.speed = sol.y.T[-1, 3]
                #
                message += "- moving<"+str(self.x)+","+str(self.y)+">"
            else:
                message += "- waiting<"+str(self.state)+">"
            #end, update time
            self.time += Ts
            status = True
        except Exception:
            message += "- ERROR moveTs"
            traceback.print_exc()
        #end
        return (status,message)

#####################################################################
#  Module for storing multiple drones (as a list) information status.
#  - process all drones per list per timestep
#  - no concurrency or parallelism (TODO: though could be implemented)
class DataDrone:
    '''
    Datastucture for holding all drones in certain airspace:
        Will need to periodically update drone location.

    TODO: doesn't handle if drones move between airspaces...
    '''

    def __init__(self, max_size=100):
        self.list_drones = []           #all drones(on ground or in air)
        self.max_drones_size = max_size #model limited airspace

    '''Processes'''
    def processAll(self, Ts):
        status = False
        message = ""
        for idrone in self.list_drones:
            #drone state machine
            if(Drone.GROUND_READY == idrone.state):
                (istatus,imessage) = idrone.launch()
            else:
                (istatus,imessage) = idrone.moveTs(Ts)
            #---
            message += imessage
            if(not istatus):
                status = False
                break
        #return overall status and message
        return (status,message)
    
    '''Operations on data'''
    def getPose(self):
        '''Position(x,y) and Orientation(yaw)'''
        list_x = []
        list_y = []
        list_heading = []
        for idrone in self.list_drones:
            list_x.append(idrone.x)
            list_y.append(idrone.y)
            list_heading.append(idrone.heading)
        return (list_x,list_y,list_heading)

    def addDrone(self, new_drone) -> bool:
        status = False
        if(self.max_drones_size > len(self.list_drones)):
            self.list_drones.append(new_drone) 
            status = True
        #return True if successful
        return status

    def removeDrone(self, id):
        status = False
        #find it, if there
        for idrone in self.list_drones:
            if(id == idrone.DRONE_ID):
                self.list_drones.remove(idrone)
                status = True
                break
        #return True if successful, drone object
        return (status,idrone)

    def airspaceCurrSize(self) -> int:
        return len(self.list_drones)
    
    def airspaceAvialableSize(self) -> int:
        return (self.max_drones_size - self.airspaceCurrSize())

#####################################################################
# TESTING MODULE
#################
if __name__ == "__main__":
    print("START TEST drone_processor.py")
    #  Uses mathplotlib. `python -m pip install -U matplotlib`
    import matplotlib.pyplot as plt             #main plotting
    import random
    #---
    seed = 12345
    Ts = 0.5              #sec, update rate
    cnt_tot = 20       #how many timesteps?
    grid_max = 10       #sim (start)environment
    grid_min = -10
    drone_sz_max = 1    #drone size
    drone_sz_min = 1
    drone_spd_max = 5   #drone speed
    drone_spd_min = 1
    #---
    rand = random.Random(seed)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = 'Times New Roman'
    fig, ax = plt.subplots()

    #setup initializations
    # Randomly assign drones to locations with random headings
    num_drones = rand.randint(10,100)
    airspace = DataDrone(num_drones)
    for icnt in range(num_drones):
        size = rand.randint(drone_sz_min,drone_sz_max)
        spd = rand.randint(drone_spd_min,drone_spd_max)
        ix = 0
        iy = 0
        idrone = Drone(size,spd,ix,iy)
        idrone.heading = rand.uniform(0,2*math.pi)
        idrone.state = Drone.GROUND_READY
        airspace.addDrone(idrone)
        print(idrone)

    #--- test drone 
    cnt = 0
    while( cnt<cnt_tot ):
        #start loop iter
        print("===Cnt[%d/%d]===" %(cnt,cnt_tot))

        try:
            message = ""
            #init print
            plt.cla()
            plt.axis([grid_min,grid_max,grid_min,grid_max])
            #process drones
            list_x = []
            list_y = []
            list_heading = []
            airspace.processAll(Ts)
            (list_x,list_y,list_heading) = airspace.getPose()
            #endloop for all drones

            #now print
            plt.scatter(list_x,list_y, c='purple',s=20, edgecolors='none', label='UAV')
            plt.pause(1)

        except Exception as e:
            print("ERROR DroneTest<%s>" %e )

        #update loop iter
        cnt += 1
    #--- end test drone

    plt.legend()
    plt.grid(True)
    plt.show()

    print("END TEST drone_processor.py")
