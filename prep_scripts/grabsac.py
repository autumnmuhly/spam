#grab sacfiles from a local or remote directory
import os
import jsonpickle
from types import SimpleNamespace
from obspy import UTCDateTime
import obspy
from obspy.clients.fdsn import Client
import statistics
import sys 
from displacement_velocity import displacement_velocity
import argparse
import subprocess
from spam import Station,Location
import glob
import shutil

class SacStream:
    def __init__(self, stanm,network,channel,lat,lon,start,stop):
        "Sac files have a sta name, min and max amp"
        self.stanm = stanm
        self.network=network
        self.channel=channel

def parseArgs():
    parser = argparse.ArgumentParser(description='creates dir, cp files, runs spam, and prepares for looper')
    parser.add_argument('-c', '--channel', help="component, R T or Z default is R", default='R' )
    parser.add_argument('-e', '--eventname', help="eventname", required=True )
    return parser.parse_args()


def readStaFile(stafile):
    sta_list = []
    command=f"awk -F, '!seen[$1>$2 ? $1 FS $2 : $2 FS $1]++' {stafile} > temp_sta"
    os.system(command)
    rm_command=f"mv -f temp_sta {stafile}"
    os.system(rm_command)
    with open('station_list_total', "r") as infile:
        #headerline = infile.readline() # ignore this one
        for line in infile:
            items = line.split()
            loc=Location(items[3],items[4])
            start=f'{items[7]}{items[8]}'
            stop=f'{items[9]}{items[10]}'
            sta_list.append(Station(items[1],items[0],loc,start,stop,items[2]))
    return sta_list

def check_grabsacfile(station,evt_name):
    """
    Removes sac files with bad amplitude value.
    takes in a single sac file. retruns a list of sacfiles that are not broken.
    """
    wd=os.getcwd()
    wd_adept=(f"/usc/data/ADEPT/{evt_name}")
    channel='R'
    stream=[]
    print('--------')
    print(wd)
    name=f'/usc/data/ADEPT/{evt_name}/{evt_name}.{station.name}.{station.netwrk}*{channel}.D.sac'
    files=glob.glob(name)
    for file in files:
        shutil.copy2(file,'.')
    stream=obspy.read(f'*.{station.name}.{station.netwrk}*{channel}.D.sac',debug_headers=True)
    for st in stream:
        start=st.stats.starttime
        newtrace=st.trim(start+1600,start+2400)
        needsDelete=False
        if newtrace.stats.npts ==0:
            print(f'{station.name}.{station.netwrk} is empty')
            needsDelete=True
            break
        max=newtrace.max()
        if min == 0 or min == "nan" or max == 0 or max == "nan":
            print(f'{station.name} needs to be deleted')
            needsDelete=True
            break
        if needsDelete == False:
            with open(f'{wd}/new_sta_list','a') as file1:
                    text=(f'{station.netwrk} {station.name} {0.0} {station.loc.lat} {station.loc.lon} {0.0} {0.0} {station.start} {sta.stop}\n')
                    os.system(f"cp /usc/data/ADEPT/{evt_name}/{evt_name}.{station.name}.{station.netwrk}*R.D.sac {wd}")
                    file1.writelines(text)
        else:
            subprocess.run(['rm', '-rf', f'*.{station.name}.{station.netwrk}*{channel}.D.sac'])

    # try:
    #     os.chdir(wd_adept)
    #     workingDir=os.getcwd()
    #     print(workingDir)
    #     print(f'*.{station.name}.{station.netwrk}*{channel}.D.sac')
    #     stream=obspy.read(f'*.{station.name}.{station.netwrk}*{channel}.D.sac',debug_headers=True) #ending of .sac file is adept specific
    # except:
    #      print(f'having trouble reading in {station.name}.{station.netwrk}')
    # if len(stream) != 0:
    #     for st in stream:
    #         start=st.stats.starttime
    #         newtrace=st.trim(start+1600,start+2400)
    #         #print(newtrace.stats.npts)
    #         if newtrace.stats.npts ==0:
    #             print(f'{station.name}.{station.netwrk} is empty')
    #             break
    #         max=newtrace.max()
    #         if min == 0 or min == "nan" or max == 0 or max == "nan":
    #             print(f'{station.name} needs to be deleted')
    #             break
    #         else:
    #             with open(f'{wd}/new_sta_list','a') as file1:
    #                     text=(f'{station.netwrk} {station.name} {0.0} {station.loc.lat} {station.loc.lon} {0.0} {0.0} {station.start} {sta.stop}\n')
    #                     os.system(f"cp /usc/data/ADEPT/{evt_name}/{evt_name}.{station.name}.{station.netwrk}*R.D.sac {wd}")
    #                     file1.writelines(text)
    os.chdir(wd)
    return


args = parseArgs()
channel=args.channel
eq_name = args.eventname
wd=os.getcwd()
all_stations=readStaFile('station_list_total')

for sta in all_stations:
    check_grabsacfile(sta,eq_name)
    
#displacement_velocity(eq_name)



