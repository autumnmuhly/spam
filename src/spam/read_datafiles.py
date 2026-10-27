import json
from datetime import datetime

from .gridpoint import Station, Location, EQ

def read_stations_adept(filepath):
    """
    Reads ADEPT style stations file. Each line is:
    network station location lat lon elevation depth firstdate lastdate
    """
    sta_list = []
    with open(filepath, "r") as infile:
        headerline = infile.readline() # ignore this one
        for line in infile:
            items = line.split()
            net = items[0]
            sta = items[1]
            locCode = items[2]
            lat = float(items[3])
            lon = float(items[4])
            loc = Location(lat, lon)
            elev = float(items[5])
            depth = float(items[6])
            firstdate = datetime.fromisoformat(items[7])
            lastdate=items[8]
            if lastdate != "None":
                lastdate = datetime.fromisoformat(items[8])
            sta = Station(net,sta,loc,firstdate,lastdate,locCode)
            sta_list.append(sta)
    return sta_list


def read_earthquakes_adept(filepath):
    """
    Reads ADEPT style earthquake file. Each line is:
    eventid datetime name mag magtype lat lon depth np1_strike np1_dip np1_rake
    """
    eq_list = []
    if filepath.startswith(("All", "ENAM")):
        with open(filepath, "r") as infile:
            headerline = infile.readline() # ignore this one
            for line in infile:
                items = line.split()
                time = datetime.fromisoformat(items[1])
                name = items[0]
                mag = float(items[3]) #all_events
                magtype = items[3]
                lat = float(items[5]) #all_events
                lon = float(items[6]) #all_events
                loc = Location(lat, lon)
                depth = float(items[7]) #all_events
                #strike = float(items[7]) if items[8] != "None" else None
                #dip = float(items[8]) if items[9] != "None" else None
                #rake = float(items[9]) if items[10] != "None" else None
                eq = EQ(loc,depth,time)
                eq_list.append(eq)
    else:
        with open(filepath, "r") as infile:
            headerline = infile.readline() # ignore this one
            for line in infile:
                items = line.split()
                #eventid = items[10]
                time = datetime.fromisoformat(items[1])
                name = items[0]
                mag = float(items[2]) 
                #mag = float(items[3]) #all_events
                magtype = items[3]
                lat = float(items[4]) 
                lon = float(items[5]) 
                #lat = float(items[5]) #all_events
                #lon = float(items[6]) #all_events
                loc = Location(lat, lon)
                #depth = float(items[7]) #all_events
                depth = float(items[6]) 
                #strike = float(items[7]) if items[8] != "None" else None
                #dip = float(items[8]) if items[9] != "None" else None
                #rake = float(items[9]) if items[10] != "None" else None
                eq = EQ(loc,depth, time)
                eq_list.append(eq)
    return eq_list

def save_arrays_json(outfilepath, array_list):
    with open(outfilepath, "w") as outf:
        json.dump(array_list, outf, indent=2,default=vars)

def load_arrays_json(infilepath):
    out_list = None
    with open(outfilepath, "w") as outf:
        out_list = json.load(outf)
    return out_list
