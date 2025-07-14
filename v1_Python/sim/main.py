# main.py
#
#  Queue UTM package drone simulation code
import sys, os
import csv
import math
#
import drone_processor as ua      #main drone class - vehicle kinematics and control
import tbov as ov                 #main tbov class - airspace objects such as constraints and operations

#for testing
import matplotlib.pyplot as plt   #main plotting
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Times New Roman'
fig, ax = plt.subplots()

#################################################
#------------------------------------------------
dir_sim_input   = "./sim_input/"
dir_sim_output  = "./sim_output/"


# read conf.txt input file ----------------------
f_log = open(dir_sim_input+"log.txt", "w+") #capture everything
try:
    f_conf = open(dir_sim_input+"conf.txt","r")
    reader = csv.reader(f_conf)
    #read data
    for iline in reader:
        tmptext_full = "".join(iline).strip()
        if( "---" == tmptext_full ):
            continue #comment
        else:
            name = iline[0]
            data = iline[1]
            if(  "seed"==name):
                pass
            elif("time step (sec)"==name):
                pass
            elif("total time steps (count)"==name):
                pass
            elif("print output every (count)"==name):
                pass
            elif("sim environment max size (meter)"==name):
                pass
            elif("")


    dir_graph_output       = reader.__next__()[1].replace(" ","") #remove whitespace
    f_log.write("graph output folder, %s\n"%dir_graph_output)
    print("graph output folder = ",dir_graph_output)
    reader.__next__()
    #------------------------
    #
    nominal_gnd_spd         = float( reader.__next__()[1] )
    f_log.write("ideal drone gnd spd (km/hr), %s\n"%nominal_gnd_spd)
    print("ideal drone gnd spd (km/hr) = ",nominal_gnd_spd)
    #convert to (m/sec) for use in sim
    nominal_gnd_spd_m_sec = nominal_gnd_spd * 1000/(60*60)
    #
    drone_setup_time        = float( reader.__next__()[1] )
    f_log.write("ideal drone setup time (sec), %s\n"%drone_setup_time)
    print("ideal drone setup time (sec) = ",drone_setup_time)
    #
    poisson_client_arr_rate = float( reader.__next__()[1] )
    f_log.write("customer request parameter (orders/hr), %s\n"%poisson_client_arr_rate)
    print("customer request parameter (orders/hr) = ",poisson_client_arr_rate)
    #convert to (orders/sec) for use in sim
    poisson_client_arr_rate = poisson_client_arr_rate / (60*60)
    #
    waypoint_clearance      = int( reader.__next__()[1] )
    f_log.write("reached waypoint distance (meter), %s\n"%waypoint_clearance)
    reader.__next__()
    #------------------------
    #
    Ts                      = float( reader.__next__()[1] )
    f_log.write("Time step (sec), %s\n"%Ts)
    print("Time step (sec) = ",Ts)
    #
    tot_icnt                = int( reader.__next__()[1] )
    f_log.write("Total number of time steps, %s\n"%tot_icnt)
    print("Total number of time steps = ",tot_icnt)
    #
    print_rate              = int( reader.__next__()[1] )
    f_log.write("Output print rate, %s\n"%print_rate)
    print("Output print rate = ",print_rate)
    reader.__next__()
    #------------------------
    #
    drones_per_depot        = int( reader.__next__()[1] )  #ideal, might change later
    f_log.write("ideal drone amount per depot, %s\n"%drones_per_depot)
    print("ideal drone amount per depot = ",drones_per_depot)
    #
    drone_ideal_width       = int( reader.__next__()[1] )
    f_log.write("ideal drone width (meter), %s\n"%drone_ideal_width)
    print("ideal drone width (meter) = ",drone_ideal_width)
    #
    drone_ideal_length     = int( reader.__next__()[1] )
    f_log.write("ideal drone length (meter), %s\n"%drone_ideal_length)
    print("ideal drone length (meter) = ",drone_ideal_length)
    reader.__next__()
    #------------------------
    #
    TBOV_width              = int( reader.__next__()[1] )
    f_log.write("TBOV width from drone center (meter), %s\n"%TBOV_width)
    print("TBOV width from drone center (meter) = ",TBOV_width)
    #
    TBOV_length             = int( reader.__next__()[1] )
    f_log.write("TBOV length from drone center (meter), %s\n"%TBOV_length)
    print("TBOV length from drone center (meter) = ",TBOV_length)
    #
    TBOV_Ts                 = float( reader.__next__()[1] )
    f_log.write("TBOV update rate (sec), %s\n"%TBOV_Ts)
    print("TBOV update rate (sec) = ",TBOV_Ts)
    #
    depot_TBOV_clearance    = int( reader.__next__()[1] )
    f_log.write("depot TBOV ignore distance (meter), %d\n"%depot_TBOV_clearance)
    reader.__next__()
    #------------------------
    #
except Exception as e:
    print("%s" %e )
    sys.exit(1)
f_conf.close()
f_log.write("Creating files for each subgraph...\n") #save individual log per igraph below

#various initializations ------------------------
size = 1            #drone box size in meters
BUFFER_size = 25    #buffer box size in meters 
flag_const_flow = False
#---
flag_flow_control = True
flag_buffer_enable = True
#---
flag_test1 = False   #TBOV and network
flag_test2 = False   #Customer Data
#---
flag_sim = True    #start main sim



#------------------------------------------------
f_log.write("---END SIMULATION---\n")
f_log.write("SIM DONE %d/%d, TOTAL TIME=%.2f\n" %(icnt+1,tot_icnt,curr_time) )
f_log.write("Total number of customer requests = %d\n" %tot_cust_cnt)
f_log.write("Total number of drones finished   = %d\n" %tot_dron_done_cnt)
f_log.write("Total number of drones flew       = %d\n" %tot_dron_cnt)
f_log.write("Total number of delay updates     = %d\n" %tot_conflict_cnt)
f_log.close()

print("DONE, check log..")
