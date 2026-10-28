#create sta file for spam if sac files already exist. must run script in directory of sac files. output is sta_info.txt
import obspy
from obspy.clients.fdsn import Client
from obspy.clients.fdsn import RoutingClient
import os
from obspy import UTCDateTime

if os.path.exists('sta_info.txt'):
    os.remove('sta_info.txt')
st = obspy.read('*.sac', debug_headers=True)
try:
    client=Client('HL')
except:
    client=RoutingClient("iris-federator")
file=open("sta_info.txt",'a+')
text=('network staname loc lat lon elv dp start end\n')
file.writelines(text)
file.close()
for sacfile in st:
    stanm=sacfile.stats.sac.kstnm.strip()+''
    stala=format(sacfile.stats.sac.stla,'.4f')
    stalo=format(sacfile.stats.sac.stlo,'.4f')
    stael=sacfile.stats.sac.stel
    stadp=sacfile.stats.sac.stdp
    netwrk=sacfile.stats.sac.knetwk
    time_beg=sacfile.stats.sac.b
    time_end=sacfile.stats.sac.e
    inventory=client.get_stations(network=netwrk,station=stanm,level='station')
    station=inventory[0][0]
    start=UTCDateTime(station.start_date).strftime("%Y-%m-%dT%H:%M:%S")
    end=station.end_date
    if end is not None:
        end=UTCDateTime(station.end_date).strftime("%Y-%m-%dT%H:%M:%S")
    location=00
    file=open("sta_info.txt",'a+')
    text=(f'{netwrk[:2]} {stanm} {location} {stala} {stalo} {stael} {stadp} {start} {end}\n')
    file.writelines(text)
    file.close()
print('Run create_evt.py if you dont have event list. If you have event list you are ready to spam')
