# path_generator.py
#
#  Closed path random generator, creates a new list as Google Earth:
#  ex: [(x,y), (altitude x,y), ...(altitude)]
#  First and last entry are looped so are special. In general [(x,y)], ignoring altitude
import sys
import csv
import random

#------------------------------------------------
dir_path_input   = "./path_input/"
dir_path_output  = "./path_output/"

f_log = open(dir_path_output+"log.txt", "w+") #capture everything (for debgging)

# read conf_path.txt input file -----------------
f_log.write("---START read conf_path.txt\n")
f_lrz_loc = ""
f_fly_loc = ""
path_use_same_LRZ = 0
path_use_same_geofence = 0
path_num_flybys = 0
path_seed = 0
#---
rand = random.Random(path_seed)
#---
try:
    f_conf = open(dir_path_input+"conf_path.txt","r")
    reader = csv.reader(f_conf)
    for iline in reader:
        #skip seperators...
        tmptext_full = "".join(iline).strip()
        if( "---" != tmptext_full ):
            tmptext = iline[0].strip() #remove leading and trailing whitespace
            #---
            if(   "file location of LRZs" == tmptext ):
                f_lrz_loc = iline[1].replace(" ","")
                f_log.write("%s,%s\n" %(tmptext,f_lrz_loc))
            elif( "file location of flybys" == tmptext ):
                f_fly_loc = iline[1].replace(" ","")
                f_log.write("%s,%s\n" %(tmptext,f_fly_loc))
            #---
            elif( "use same LRZ" == tmptext ):
                path_use_same_LRZ = int( iline[1].replace(" ","") )
                f_log.write("%s,%d\n" %(tmptext,path_use_same_LRZ))
            elif( "use same geofence" == tmptext ):
                path_use_same_geofence = int( iline[1].replace(" ","") )
                f_log.write("%s,%d\n" %(tmptext,path_use_same_geofence))
            elif( "number of flybys" == tmptext ):
                path_num_flybys = int( iline[1].replace(" ","") )
                f_log.write("%s,%d\n" %(tmptext,path_num_flybys))
            #---
            elif( "random seed" == tmptext ):
                path_seed = int( iline[1].replace(" ","") )
                f_log.write("%s,%d\n" %(tmptext,path_seed))
            ####
            else:
                f_log.write("NOT READ:%s\n" %tmptext_full)
except Exception as e:
    f_log.write("%s\n" %e )
    sys.exit(1)
f_conf.close()
f_log.write("---END read conf_path.txt\n")

#create placemarkers ----------------------------
#create LRZ locations
f_log.write("---START LRZ\n")
igeofence = 0
Loc_LRZ = []
try:
    f_lrz_data = open(dir_path_input+f_lrz_loc, "r")
    reader = csv.reader(f_lrz_data)
    for iline in reader:
        #new geofence?
        if( "LRZ" == iline[0] ):
            #no, part of current geofence...
            ilrz = int( iline[1] )
            ix   = float( iline[2] )
            iy   = float( iline[3] )
            Loc_LRZ[igeofence-1].append( (ilrz, ix,iy) )
            f_log.write("LRZ,%d,%f,%f\n" %(ilrz,ix,iy))
        else:
            #yes, new geofence...
            Loc_LRZ.insert(igeofence,[])
            igeofence = igeofence + 1
            f_log.write("G%d\n" %igeofence)
except Exception as e:
    f_log.write("%s\n" %e )
    sys.exit(1)
f_lrz_data.close()
num_geofence = igeofence
f_log.write("number of geofences %d\n" %num_geofence)
f_log.write("---END LRZ\n")

#create flyby locations
f_log.write("---START flyby\n")
Loc_fly = []
try:
    f_fly_data = open(dir_path_input+f_fly_loc, "r")
    reader = csv.reader(f_fly_data)
    for iline in reader:
        ifly = int( iline[1] )
        ix   = float( iline[2] )
        iy   = float( iline[3] )
        Loc_fly.append( (ifly, ix,iy) )
        f_log.write("flyby,%d,%f,%f\n" %(ifly,ix,iy))
except Exception as e:
    f_log.write("%s\n" %e )
    sys.exit(1)
f_lrz_data.close()
num_flybys = len(Loc_fly)
f_log.write("number of flybys %d\n" %num_flybys)
f_log.write("---END flyby\n")

#create paths -----------------------------------
f_log.write("---START paths\n")
f_out_path = open(dir_path_output+"path.txt", "w")
Path = []
igeocnt=0
#create random path by picking one or two lrz and one or more flybys, TODO: might revist...
for igeofence in Loc_LRZ:
    for iLRZ in igeofence:
        iPath = []
        #---
        ilrz = iLRZ[0]
        istx = iLRZ[1]
        isty = iLRZ[2]
        iPath.append((istx,isty)) #start loc
        f_log.write("path,%d,%d,start,%f,%f" %(igeocnt,ilrz,istx,isty)) #st continues...
        #have st, need flybys (generate based on config)
        for icnt in range(path_num_flybys):
            ifly = Loc_fly[ rand.randint(0, num_flybys-1) ]
            ix = ifly[1]
            iy = ifly[2]
            iPath.append((ix,iy)) #flyby loc
            f_log.write(",%f,%f" %(ix,iy)) #continues...
        #now goto LRZ
        jlrz = ilrz
        jgeocnt = igeocnt
        if( (1 == path_use_same_LRZ) or (1 == path_use_same_geofence and 1 == len(igeofence)) ):
            ienx = istx
            ieny = isty #same end==start
        else:
            if( 1 == path_use_same_geofence ):
                jgeofence = igeofence.copy() 
                jgeofence.remove(iLRZ) #remove same LRZ
            else:
                oLoc_LRZ = Loc_LRZ.deepcopy()
                oLoc_LRZ.remove(igeofence) #remove same geofence
                jgeofence = rand.choice(oLoc_LRZ)
            jLRZ = rand.choice(jgeofence)
            jlrz = jLRZ[0]
            ienx = jLRZ[1]
            ieny = jLRZ[2]
        iPath.append((ienx,ieny)) #end loc
        f_log.write(",%f,%f,end,%d,%d\n" %(ienx,ieny,jgeocnt,jlrz)) #en of path
        #---
        Path.append(iPath)
        tmptext_path = str(Path[-1])+"\n"
        f_out_path.write(tmptext_path)
    #endfor
    igeocnt = igeocnt + 1
#endfor
f_out_path.close()
num_paths = len(Path)
f_log.write("number of paths %d\n" %num_paths)
f_log.write("---END paths\n")

####################
f_log.close()
print("DONE")
