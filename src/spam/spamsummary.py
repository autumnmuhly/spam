#!/usr/bin/env python

import argparse
import os
import datetime
import sys
import json
from types import SimpleNamespace
from spam import ArrayToEqlist,Gridpoint,EQ

def summary(args):
    infilename = "spam.json"
    with open(infilename, "r") as inf:
        mydata=json.load(inf)
    good_arrays=[ArrayToEqlist.from_json(arr) for arr in mydata['good_arrays']]
    grid_array=[Gridpoint.from_json(pt) for pt in mydata['grid_array']]
    eq_list=[EQ.from_json(eq) for eq in mydata['eq_list']]
    print(f"Array radius: {mydata.arrayradius}")
    print(f"Grid spacing: {mydata.radius_point_deg}")
    print(f"Num grid points: {len(grid_array)}")
    print(f"Num Earthquakes: {len(eq_list)}")
    print(f"Good Arrays: {len(good_arrays)}")
    if args.arrays:
        for arr_eq in good_arrays:
            arr = arr_eq.array
            print(f"  {arr.pt.loc.lat:0.2f}/{arr.pt.loc.lon:0.2f} {arr.basestation.netwrk}_{arr.basestation.name} {len(arr.sta_list)} stations, {len(arr_eq.eqlists)} earthquakes")


def parseArgs():
    parser = argparse.ArgumentParser(prog='SpamCalc',
                    description='Finds arrays for beamforming',
                    epilog='Text at the bottom of help')
    parser.add_argument('-f', '--spamfile', default="spam.json", help="input file")
    parser.add_argument('--arrays', action='store_true', help="print arrays")

    return parser.parse_args()


def main():
    args = parseArgs()
    return summary(args)

if __name__ == '__main__':
    sys.exit(main())
