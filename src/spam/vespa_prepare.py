#!/usr/bin/env python
#run this file after spamcalc to get files needed to run beamforming script
import json
import os
import argparse
from spam import ArrayToEqlist
import sys

def parseArgs():
    parser = argparse.ArgumentParser(description='extracts the files needed to beam form from json files')
    parser.add_argument('-f', '--filename', help="which json file to read in", default='spam.json')
    return parser.parse_args()

def prepare_vespa():
    args = parseArgs()
    infilename = "spam.json"
    with open(infilename, "r") as inf:
        mydata=json.load(inf)
    good_arrays=[ArrayToEqlist.from_json(arr) for arr in mydata['good_arrays']]
    if os.path.exists('grid_pts'):
        os.remove('grid_pts')
    if os.path.exists('station_list_total'):
        os.remove('station_list_total')
    if os.path.exists('base_stations'):
        os.remove('base_stations')
    with open("base_stations",'w') as file1, open("grid_pts",'w') as file2, open('station_list_total','w') as file3:
        count_array=0
        sta_list_total=[]
        for arr in good_arrays:
            count_array+=1
            #create base station list
            bs_text={f'{arr.basestation.netwrk} {arr.basestation.name} {format(arr.basestation.loc.lat,'.4f')} {format(arr.basestation.loc.lon,'.4f')}\n'}
            file1.writelines(bs_text)
            #create gridpoint list
            lat_array=format(arr.array.pt.loc.lat,'.4f')
            lon_array=format(arr.array.pt.loc.lon,'.4f')
            gp_text=(f'{count_array} {lat_array} {lon_array}\n')
            file2.writelines(gp_text)
            #create station list
            for sta in arr.good_sta_list:
                sta_list_total.append(sta)
                text=(f'{sta.netwrk} {sta.name} {0.0} {sta.loc.lat} {sta.loc.lon} {0.0} {0.0} {sta.start} {sta.stop}\n')
                file3.writelines(text)
    os.system("awk '!seen[$0]++' station_list_total > temp")
    os.system("mv temp station_list_total")
    return 

def main():
    prepare_vespa()

if __name__ == '__main__':
    sys.exit(main())