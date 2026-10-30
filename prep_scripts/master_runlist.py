import os
import argparse
from obspy import UTCDateTime
from datetime import datetime, timezone
from displacement_velocity import displacement_velocity
import subprocess

def parseArgs():
    parser = argparse.ArgumentParser(description='creates dir, cp files, runs spam, and prepares for looper')
    parser.add_argument('-e', '--evtlist', help="list of events", required=True)
    return parser.parse_args()



def formatEQList(eventfile):
    event_list=[]
    with open(eventfile, "r") as infile:
        for line in infile:
            item=line.split()
            if len(item)>1:
                print(line)
                line=line.strip()
                # ID=datetime.strptime(line.strip(), "%Y-%m-%d %H:%M").strftime('%Y-%m-%d %H:%M')
                ID=datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
                ID=ID.strftime('%Y%m%d%H%M')
                # print(ID)
                # print('-----')
                # yearmon=ID.strftime('%Y%m%d')
                # dhour=ID.strftime('%H:%M')
                # ID=str(yearmon)+str(dhour)
                event_list.append(ID)
            if len(item)==1:
                print('correctly formated already:)')
                event_list.append(line.strip())
    subprocess.run(['rm', '-rf', f'{eventfile}'])
    with open(eventfile, 'w') as infile:
        for evt in event_list:
            text=(f'{evt}\n')
            infile.writelines(text)
    return event_list

def run_spam(event_ID):
    wd=os.getcwd()
    for evt in event_ID:
        print(evt)
        try:
            # os.mkdir(evt)
            os.chdir(evt)
            # subprocess.run(['cp', '/home/amuhly/SmKS/majorarc/info_new/All.stations', '.'])
            subprocess.run(['cp', f'/usc/data/ADEPT/Info/{evt}.event', '.'])
            # For yellowstone
            #os.system(f'spamcalc -s All.stations -e {evt}.event --minsta 20 --grid 40000 --arrayradius 1.4 -p SKS,SKKKKS --region -98 -83 33 41')
            # os.system(f'spamcalc -s All.stations -e {evt}.event --minsta 20 --grid 40000 --arrayradius 1.0 -p SKKKKS')
            # os.system(f'prepvespa')
            os.system(f'python3 /home/amuhly/spam/prep_scripts/grabsac.py -e {evt}')
            os.system("mv new_sta_list station_list_total")
            displacement_velocity(evt)
        except:
            print(f'directory already exists {evt}')
        os.chdir(wd)



args = parseArgs()
eventfile=args.evtlist
evt_list=formatEQList(eventfile)
run_spam(evt_list)

