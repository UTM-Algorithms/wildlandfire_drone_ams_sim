/* path_generator.cpp
 *
 * Closed path random generator, creates a new list as Google Earth:
 * ex: [(x,y), (altitude x,y), ...(altitude)]
 * First and last entry are looped so are special. In geeral [(x,y)], ignoring altitude
 */
#include <iostream>
#include <fstream>
#include <cstdlib>
#include <string>

int main(int argc, char *argv[]) {
    //-------------------------------------------
    std::string name_prog(argv[0]);
    std::string dir_path_input  = "./path_input/";
    std::string dir_path_output = "./path_output/";

    //std::cout << name_prog << std::endl;

    // Set output for error and log messages
    std::ofstream err(name_prog + ".err");
    std::cerr.rdbuf(err.rdbuf());
    std::ofstream log(name_prog + ".log");
    std::clog.rdbuf(log.rdbuf());

    //std::cerr << "error" << std::endl;
    //std::clog << "log" << std::endl;

    // read conf_path.txt input file ------------
    std::clog << "---START read conf_path.txt\n";
    std::string f_lrz_loc = "";
    std::string f_fly_loc = "";
    int path_use_same_LRZ = 0;
    int path_use_same_geofence = 0;
    int path_num_flybys = 0;
    int path_seed = 0;
    //---
    std::srand(path_seed);



    // close and clean up all -------------------
    err.close();
    log.close();
}