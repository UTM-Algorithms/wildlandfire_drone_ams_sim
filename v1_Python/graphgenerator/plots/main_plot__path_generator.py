# plot__path_generator.py
#
#  plots waypoint locations, i.e. lrzs and flybys.
#  Also displays other information such as distance and potential paths.
import matplotlib.pyplot as plt
import csv

#------------------------------------------------
dir_plot_input   = "../path_output/"
dir_plot_output  = dir_plot_input

f_log_path = open(dir_plot_input+"log.txt", "r") #all data in here
f_log_plot = open(dir_plot_output+"log_plot.txt", "w+") #capture everything (for debgging)

# extract LRZ, flyby, paths ---------------------
Loc_LRZ = [] #item=(lrz_id,x,y)
Loc_fly = [] #item=(fly_id,x,y)
Path = [] #sequence of (x,y)
#---
igeofence = 0
num_geofence = 0
ptmptext_full = ""
#---
reader = csv.reader(f_log_path)
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
                Loc_LRZ[igeofence-1].append( (ilrz, ix,iy) )
                f_log_plot.write("LRZ,%d,%f,%f\n" %(ilrz,ix,iy))
            elif("G" == tmptext_full[0]): #make sure first char == "G"
                #yes, new geofence...
                Loc_LRZ.insert(igeofence,[])
                igeofence = igeofence + 1
                f_log_plot.write("G%d\n" %igeofence)
        else:
            ptmptext_full = ""
        #endif
        num_geofence = igeofence
    elif("---START flyby" == tmptext_full or "---START flyby" == ptmptext_full):
        if("---START flyby" == tmptext_full): ptmptext_full = "---START flyby"
        if("---END flyby" != tmptext_full):
            if( "flyby" == iline[0] ):
                ifly = int( iline[1] )
                ix   = float( iline[2] )
                iy   = float( iline[3] )
                Loc_fly.append( (ifly, ix,iy) )
                f_log_plot.write("flyby,%d,%f,%f\n" %(ifly,ix,iy))
        else:
            ptmptext_full = ""
        #endif
    elif("---START paths" == tmptext_full or "---START paths" == ptmptext_full):
        if("---START paths" == tmptext_full): ptmptext_full = "---START paths"
        if("---END paths" != tmptext_full):
            if("path" == iline[0]):
                iPath = []
                for icnt in range(4,len(iline)-3,2):
                    ix = iline[icnt  ]
                    iy = iline[icnt+1]
                    iPath.append((ix,iy))
                Path.append(iPath)
                f_log_plot.write("path,%s\n" %str(Path[-1]))
        else:
            ptmptext_full = ""
        #endif
    #endif

#------------------------------------------------
# create plot of all depots and waypoints
#------------------------------------------------
# 2D top-view of simulation map
fig = plt.figure()
ax = fig.add_subplot(111) #dummy placeholder, used to get "ax"
plt.cla()

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
for iPath in Path:
    cnt = cnt + 1
    xdata_path_list = []
    ydata_path_list = []
    for idata in iPath:
        ix = float(idata[0])
        iy = float(idata[1])
        xdata_path_list.append( ix )
        ydata_path_list.append( iy )
    plt.plot(xdata_path_list,ydata_path_list, c='C'+str(cnt),linewidth=0.25)
#END paths

plt.legend()
plt.grid(True, linewidth=0.15)
ax.set_aspect('equal', adjustable='box')
#plt.axis([-0.1,1.1, -0.1,1.1])
#plt.xlabel("meters")
#plt.ylabel("meters")
plt.title("Full Simulation Map")
plt.savefig(dir_plot_output+'Figure_All.png')
print("Saved Figure for all graphs")

