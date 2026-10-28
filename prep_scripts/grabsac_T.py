#grab sacfiles from a local or remote directory
import os
import jsonpickle
from types import SimpleNamespace
from obspy import UTCDateTime
import obspy
from obspy.clients.fdsn import Client
import statistics
import argparse
from datetime import datetime, timezone



class SacStream:
    def __init__(self, stanm, network):
        "Sac files have a sta name, min and max amp"
        self.stanm = stanm
        self.network=network
        self.depmin = [] #for later if we need it ?
        self.depmax = [] #for later if we need it ?

def readStaFile(stafile):
    sta_list = []
    #check for station duplicates using awk 
    command=f"awk -F, '!seen[$1>$2 ? $1 FS $2 : $2 FS $1]++' {stafile} > temp_sta"
    os.system(command)
    rm_command=f"mv -f temp_sta {stafile}"
    os.system(rm_command)
    #extract sta info from file
    with open('station_list_total', "r") as infile:
        headerline = infile.readline() # ignore this one
        for line in infile:
            items = line.split()
            sta_list.append(SacStream(items[0],items [1]))
    return sta_list

def create_stalist():
    sta_list=[]
    os.system("ls *.sac > sacfiles")


def grab_sacfiles(checked_list,evt_name):
    for sacfile in checked_list:
        os.system(f"cp /usc/data/ADEPT/{evt_name}/{evt_name}.{sacfile.stanm}.{sacfile.network}*T.D.sac .")


def parseArgs():
    parser = argparse.ArgumentParser(description='creates dir, cp files, runs spam, and prepares for looper')
    parser.add_argument('-e', '--evtlist', help="list of events", required=True)
    return parser.parse_args()

def event_list(eventfile):
    event_ID=[]
    with open(eventfile, "r") as infile:
#        headerline = infile.readline()
        # for line in infile:
        #     items = line.split()
        #     date=items[0]
        #     time=items[1]
        #     ID=datetime.strptime(f'{date} {time}', "%Y-%m-%d %H:%M:%S")
        #     ID=UTCDateTime(ID).strftime("%Y%m%d%H%M")
        #     event_ID.append(ID)
        for line in infile:
            items=line.split()
            ID=items[0]
            event_ID.append(ID)
    return event_ID



args = parseArgs()
eventfile=args.evtlist
evt_list=event_list(eventfile)
home_dir=os.getcwd()
for evt in evt_list:
    os.chdir(evt)
    #heck_stalist=check_sacfiles('station_list_total',evt)
    sta_list=readStaFile('station_list_total')
    #print(sta_list)
    #grab_sacfiles(check_stalist,evt)
    os.chdir(home_dir)