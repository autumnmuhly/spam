import argparse
import jsonpickle
from multiprocessing import Pool
import functools
import os
from datetime import datetime
from .mesh_create import find_neighbors,fibonacci_sphere,create_gridpoint
from .mesh_setup import latlon_cartesian,cart_latlon, radius_per_gridpoint
from .gridpoint import Gridpoint,Station,EQ,Location,MetaData
from .array import Array,form_all_array,ArrayToEqlist,EqtoArrayList,EqGridAssignment,form_eq,items_in_dist,is_array_gp_okay,calcBasestation
from .distaz import DistAz
from .read_datafiles import (
    read_stations_adept, read_earthquakes_adept,
    load_arrays_json, save_arrays_json
    )
from .taup import (
   phase_dist_range, taup_time, taup_phase
   )
from .arrConfig import calcArthCenter
import json

def calc_one_array(phaseToDist, eq_list, min_station, min_eq_needed, arr ):
    arrToEQ = ArrayToEqlist(arr)
    #loop over evts and arrays and check if distance range is met
    for phase, dist in phaseToDist.items():
        for evt in eq_list:
            arrToEQ.check_eq(evt,dist,min_station)
    return arrToEQ
 
    
def calc_good_arrays(phase_list,
                    array_list,
                    eq_list,
                    min_station=1,
                    min_eq_needed=1):
    phaseToDist = {}
    for phase in phase_list:
        # Distance range of phase, from TauP
        dist = phase_dist_range(phase,sourcedepth=0,model='prem')
        #dist = (60, 185)
        print(dist)
        if dist is None:
            print(f"Cannot determine phase distance range for {phase}")
            sys.exit(0)
        phaseToDist[phase] = dist
        #print(f'this is whats in phaseToDist {phaseToDist}')
    partial_calc = functools.partial(calc_one_array, phaseToDist, eq_list, min_station, min_eq_needed)

    with Pool(processes=(os.process_cpu_count()-1)) as pool:
        arrayToeq = pool.map(partial_calc, array_list)
    #loop over array in array list to decided if enough eq exist to be considered an array
    good_arrays=[]
    for arr in arrayToeq:
        if arr.eqcount>=min_eq_needed:
            good_arrays.append(arr)

    if len(good_arrays) == 0:
        print(f"no arrays pass min eq {min_eq_needed}")
    return good_arrays

def parseArgs():
    parser = argparse.ArgumentParser(prog='SpamCalc',
                    description='Finds arrays for beamforming',
                    epilog='Text at the bottom of help')
    parser.add_argument('-p', '--phases', nargs="+", help="phases of interest", required=True)
    parser.add_argument('-s', '--stations',required=True)
    parser.add_argument('-e', '--earthquakes',required=True)
    parser.add_argument('--grid', type=int, default=40000, help="number of grid points over earth")
    parser.add_argument('--region', type=int, nargs=4, help="restrict grid points to WESN box")
    parser.add_argument('--arrayradius', type=float, default=1.0, help="radius of array in degrees")
    parser.add_argument('--minsta', type=int, default=1, help="min number of stations near a grid point to form an array")
    parser.add_argument('--mineq', type=int, default=1, help="min number of earthquakes at an array to be successful")
    parser.add_argument('-o', '--outfile', default="spam.json", help="output file")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose output")
    return parser.parse_args()


def run_calc(args):

    version = 'version 0.0.2Beta'
    radius_point_deg=radius_per_gridpoint(args.grid)
    print(f'array radius, {args.arrayradius} and gridpoint spacing, {radius_point_deg}')
    if args.arrayradius < radius_point_deg:
        print(f"WARNING: array radius, {args.arrayradius} less than gridpoint spacing, {radius_point_deg}")
    grid_array=create_gridpoint(args.grid)
    if args.verbose: print("grid created")
    if args.region:
        region_grid = []
        west = args.region[0]
        east = args.region[1]
        south = args.region[2]
        north = args.region[3]
        for g in grid_array:
            if west <= g.loc.lon <= east and south <= g.loc.lat <= north:
                region_grid.append(g)
        grid_array = region_grid

    station_list=read_stations_adept(args.stations)
    if args.verbose: print(f"{len(station_list)} stations")
    eq_list=read_earthquakes_adept(args.earthquakes)
    if args.verbose: print(f"{len(eq_list)} earthquakes")

    array_list=form_all_array(station_list, grid_array, args.arrayradius, args.minsta)
    if len(array_list) == 0:
        print(f"no arrays pass for radius {args.arrayradius} deg with  min {args.minsta} stations")
        return 1
    array_list_checked=[]
    for arr in array_list:
        if is_array_gp_okay(arr,args.arrayradius) == True:
            array_list_checked.append(arr)
    array_list=array_list_checked


    print(f'this is the len of array list {len(array_list)}')
    good_arrays = calc_good_arrays(args.phases, array_list, eq_list, args.minsta, args.mineq)
    print(f'this is the len of how many arrays are good {len(good_arrays)}')


    with open('eq_list','w') as file1:
        for arr in good_arrays:
            calcArthCenter(arr)
            calcBasestation(arr)
            #print(f'this is base station {arr.basestation}')
            for evt in arr.eqlists:
                #eq sub array here we create eq to array pair. and throw away stations that dont work for that eq. like time interval doesnt overlap
                text=(f'{evt.time} \n')
                file1.writelines(text)

    creationDate=datetime.now()
    creationDate=creationDate.isoformat()
    metaData=MetaData(version,creationDate)
    
    #for arr in good_arrays:
        #print(arr.ArrayToEqlist)
        #for sta in arr.array.sta_list:
            #print(sta.name)

    os.system("awk -F, '!seen[$1>$2 ? $1 FS $2 : $2 FS $1]++' eq_list | awk  '{print $0}' > temp_sta")
    os.system("mv -f temp_sta eq_list")
    # mydata={
    #     "array_list":array_list,
    #     "grid_array": grid_array,
    #     "good_arrays": good_arrays,
    #     "phase": args.phases,
    #     "dist": phase_dist_range(args.phases,model='prem'),
    #     "arrayradius": args.arrayradius,
    #     "min_sta_per_array": args.minsta,
    #     "min_eq_at_array": args.mineq,
    #     "eq_list": eq_list,
    #     "station_list": station_list,
    #     "radius_point_deg": args.arrayradius,
    #     "radius_of_earth": 6371,
    #     "num_pts": args.grid,
    #     "meta_data":metaData
    # }
        
        
    # with open(args.outfile, "w") as outf:
    #     outf.write(jsonpickle.encode(mydata))
    # return 0
    mydata={
        "array_list":[arr.to_json() for arr in array_list],
        "grid_array":[pt.to_json() for pt in grid_array],
        "good_arrays":[arr.to_json() for arr in good_arrays],
        "phase":args.phases,
        "dist":phase_dist_range(args.phases, model="prem"),
        "arrayradius":args.arrayradius,
        "min_sta_per_array":args.minsta,
        "min_eq_at_array":args.mineq,
        "eq_list":[eq.to_json() for eq in eq_list],
        "station_list":[sta.to_json() for sta in station_list],
        "radius_point_deg":args.arrayradius,
        "radius_of_earth":6371,
        "num_pts":args.grid,
        "meta_data":metaData.to_json()
        }
    with open(args.outfile, "w") as outf:
        json.dump(mydata, outf, indent=4)
    return 0


def main():
    args = parseArgs()
    return run_calc(args)

if __name__ == '__main__':
    sys.exit(main())
