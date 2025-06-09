# mission_processor.py
#
#  Module: mission generator for drone
#  Module: 
import traceback
import csv
import sys

#####################################################################
#  Module for generating trajectory based on line of sight and constant
#  speed movement of point-mass vehicle.
class DroneMissionPlanner:
    '''
    Simple Drone Mission Planner: 
        creates 3d trajectory (2d space, 1d time).
        Mission is from lrz->lrz (can be same or different)
    '''

    def __init__(self):
        self.Xr=[]
        self.Yr=[]
        self.Tr=[]
        self.Hr=[]
        #
        self.Loc_LRZ=[]
        self.Loc_fly=[]
        self.Path = []
        #
        self.num_geofence = -1
        self.num_lrz = -1
        self.num_flyby = -1
        self.num_path = -1
        #
        self.loadedData = False

    '''Initialization methods'''

    def loadData(self, file):
        status = False
        message = "DroneMissionPlanner: load data connection file: "+file+"\n"
        #---
        igeofence = 0
        ptmptext_full = ""
        #---
        try:
            f = open(file,"r")
            reader = csv.reader(f)
            for iline in reader:
                tmptext_full = "".join(iline).strip()
                #find group...
                if(  "---START LRZ" == tmptext_full or "---START LRZ" == ptmptext_full):
                    if("---START LRZ" == tmptext_full): ptmptext_full = "---START LRZ"
                    if("---END LRZ" != tmptext_full):
                        #new geofence?
                        if( "LRZ" == iline[0] ):
                            #no, part of current geofence...
                            ilrz = int( iline[1] )
                            ix   = float( iline[2] )
                            iy   = float( iline[3] )
                            self.Loc_LRZ[igeofence-1].append( (ilrz, ix,iy) )
                            self.num_lrz += 1
                            message += f"LRZ,{ilrz},{ix},{iy}\n"
                        elif("G" == tmptext_full[0]): #make sure first char == "G"
                            #yes, new geofence...
                            self.Loc_LRZ.insert(igeofence,[])
                            igeofence += 1
                            message += f"G{igeofence}\n"
                    else:
                        ptmptext_full = ""
                    #endif
                    self.num_geofence = igeofence
                elif("---START flyby" == tmptext_full or "---START flyby" == ptmptext_full):
                    if("---START flyby" == tmptext_full): ptmptext_full = "---START flyby"
                    if("---END flyby" != tmptext_full):
                        if( "flyby" == iline[0] ):
                            ifly = int( iline[1] )
                            ix   = float( iline[2] )
                            iy   = float( iline[3] )
                            self.Loc_fly.append( (ifly, ix,iy) )
                            self.num_flyby += 1
                            message += f"flyby,{ifly},{ix},{iy}\n"
                    else:
                        ptmptext_full = ""
                    #endif
                elif("---START paths" == tmptext_full or "---START paths" == ptmptext_full):
                    if("---START paths" == tmptext_full): ptmptext_full = "---START paths"
                    if("---END paths" != tmptext_full):
                        if("path" == iline[0]):
                            #start lrz(geofence#,lrz#)
                            igeofence = int(iline[1])
                            ilrz =      int(iline[2])
                            #flyby waypoints
                            iPath = []
                            for icnt in range(4,len(iline)-3,2):
                                ix = float(iline[icnt  ])
                                iy = float(iline[icnt+1])
                                iPath.append((ix,iy))
                            #end lrz(geofence#,lrz#)
                            jgeofence = iline[1]
                            jlrz = iline[2]
                            #combine together([ig,ilrz,jg,jlrz],Path[])
                            self.Path.append( ((igeofence,ilrz,jgeofence,jlrz),iPath) )
                            self.num_path += 1
                            message += f"path,{str(self.Path[-1])}\n"
                    else:
                        ptmptext_full = ""
                    #endif
                #endif
            f.close()
            #everything went well...
            status = True
            self.loadedData = True
        except:
            message += "- ERROR loadData"
            traceback.print_exc()
        return (status,message)
    
    '''Create Routes'''

    def generateRoute(self, igeofence,ilrz, jgeofence=-1,jlrz=-1) -> list:
        '''TODO: currently just returns path from graphgenerator, ignores j part'''
        route = -1
        status = False
        message = "DroneMissionPlanner: "+f"geo<{igeofence}> lrz<{ilrz}>\n"
        if(self.num_geofence > 0):
            for iPath in self.Path:
                iloc = iPath[0]
                message += f"{iloc}\n"
                stgeofence = int(iloc[0])
                stlrz =      int(iloc[1])
                engeofence = int(iloc[2]) #currenly ignore
                enlrz =      int(iloc[3]) #currently ignore
                #---
                if(stgeofence==igeofence and stlrz==ilrz):
                    route = iPath[1]
                    message += f"{route}\n"
                    status = True
                    break
        #return completed route or -1
        return (route,status,message)
    
#####################################################################
#  Module for storing multiple missions (one mission per drone) (as a list) information status.
#  - process all missions per list per timestep (TODO: add more missions per drone)
#  - no concurrency or parallelism (TODO: though could be implemented)
class DataDroneMissionPlanner:
    from drone_processor import Drone
    '''
    Datastucture for holding all drones' missions:
        Event-driven only need to update mission per situation.
    '''

    def __init__(self, file: str):
        self.dic_dronemissions = {} #all missions(one per drone)
        #file = "../graphgenerator/path_output/log.txt"
        self.missions = DroneMissionPlanner()
        (status,message) = self.missions.loadData(file)
        if(not status):
            print("ERROR: %s" %message)
            sys.exit(1)

    '''Processes'''
    def assignMission(self, drone: Drone, igeofence: int, ilrz: int):
        status = False
        message = "DataDroneMissionPlanner assignMission: "
        if(drone.GROUND_NO_OPS == drone.state):
            #...all good and not assigned mission
            (iPath,tstatus,tmessage) = self.missions.generateRoute(igeofence,ilrz)
            if(tstatus):
                self.dic_dronemissions[drone.DRONE_ID] = iPath #key=drone_id, value=path
                message += tmessage
                (tstatus,tmessage) = drone.assignMission()
                message += tmessage
                if(tstatus): status = True
            else:
                message += f"ERROR: not generated path: {iPath}\n{tmessage}\n"
            #END path
        return (status,message)
    
    def readyMission(self, drone: Drone):
        status = False
        message = "DataDroneMissionPlanner readyMission: "
        if(drone.GROUND_WAIT == drone.state):
            #...all good and not ready to launch
            drone.state = drone.GROUND_READY
            message += "- ready\n"
            status = True
        else:
            message += f"ERROR: incorrect state: {drone.state}\n"
        #endcheck
        return (status,message)

#####################################################################
# TESTING MODULE
#################
if __name__ == "__main__":
    print("START TEST mission_processor.py")
    #  Uses mathplotlib. `python -m pip install -U matplotlib`
    import matplotlib.pyplot as plt             #main plotting
    import random
    from drone_processor import Drone
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

    file = "../graphgenerator/path_output/log.txt"
    datamissions = DataDroneMissionPlanner(file)
    missions = datamissions.missions
    num_geofence = missions.num_geofence
    Loc_LRZ = missions.Loc_LRZ
    Loc_fly = missions.Loc_fly

    # LRZ locations data
    xdata_lrz_list = []
    ydata_lrz_list = []
    cnt=0
    for igeofence in range(num_geofence):
        for idata in Loc_LRZ[igeofence]:
            cnt += 1
            ix = idata[1]
            iy = idata[2]
            plt.text(ix,iy,"LRZ"+str(cnt))
            xdata_lrz_list.append( ix )
            ydata_lrz_list.append( iy )
    plt.scatter(xdata_lrz_list,ydata_lrz_list, c='orange',s=80, edgecolors='none', label='LRZ')
    #END LRZ

    # flyby locations data
    xdata_fly_list = []
    ydata_fly_list = []
    cnt=0
    for idata in Loc_fly:
        cnt += 1
        ix = idata[1]
        iy = idata[2]
        plt.text(ix,iy,"w"+str(cnt))
        xdata_fly_list.append( ix )
        ydata_fly_list.append( iy )
    plt.scatter(xdata_fly_list,ydata_fly_list, c='yellow',s=5, edgecolors='black', label='waypoint')
    #END flyby

    # paths data
    cnt=0
    for igeofence in range(num_geofence):
        for idata in Loc_LRZ[igeofence]:
            size = rand.randint(drone_sz_min,drone_sz_max)
            spd = rand.randint(drone_spd_min,drone_spd_max)
            ix = 0
            iy = 0
            new_drone = Drone(size,spd,ix,iy)
            print("drone st: %s\n" %new_drone)
            #---
            ilrz = idata[0]
            (status,message) = datamissions.assignMission(new_drone,igeofence,ilrz)
            if(status):
                cnt += 1
                xdata_path_list = []
                ydata_path_list = []
                iPath = datamissions.dic_dronemissions[new_drone.DRONE_ID]
                if(0 < len(iPath)):
                    print("drone mission: %s\n" %new_drone)
                    for ipathdata in iPath:
                        ix = float(ipathdata[0])
                        iy = float(ipathdata[1])
                        xdata_path_list.append( ix )
                        ydata_path_list.append( iy )
                else:
                    print("ERRORTEST: not generated path: %s\n%s" %(iPath,message))
                plt.text(xdata_path_list[0]+random.uniform(0,0.2),ydata_path_list[0]+random.uniform(0,0.2),"p"+str(cnt), c='C'+str(cnt))
                plt.plot(xdata_path_list,ydata_path_list, c='C'+str(cnt),linewidth=0.25)
            #endif
            datamissions.readyMission(new_drone)
            print("drone ready: %s\n" %new_drone)
    #END paths

    #---end
    plt.legend()
    plt.grid(True)
    plt.show()

    print("END TEST mission_processor.py")