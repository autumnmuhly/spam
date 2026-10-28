#Creates an eq catalog given in the format needed for spam. output is file evt_info.txt
import obspy
from obspy.clients.fdsn import Client
from obspy.core.utcdatetime import UTCDateTime
import os
from obspy import read_events
if os.path.exists('evt_info.txt'):
    os.remove('evt_info.txt')
client = Client("IRIS")
starttime = UTCDateTime("2011-11-15")
endtime = UTCDateTime("2011-11-15")
min_mag=5.5
min_depth=50
catalog=client.get_events(starttime=starttime, endtime=endtime,minmagnitude=min_mag,mindepth=min_depth)
print(catalog)

for evt in catalog:
    event=evt.origins[0]
    evtid=event.resource_id
    lat=event.latitude
    lon=event.longitude
    time=UTCDateTime(event.time).strftime("%Y-%m-%dT%H:%M:%S")
    name=UTCDateTime(event.time).strftime("%Y%m%dT%H%M%S")
    depth=event.depth
    np1_strike=0
    np1_dip=0
    np1_rake=0
    magnitudes=evt.magnitudes
    magnitudes=evt.magnitudes[0]
    mag=magnitudes.mag
    magtype=magnitudes.magnitude_type
    print(evtid, time, mag, magtype, lat, lon, depth, np1_strike, np1_dip, np1_rake)
    file=open("evt_info.txt",'a+')
    text=(f'{evtid} {time} {name} {mag} {magtype} {lat} {lon} {depth} {np1_strike} {np1_dip} {np1_rake}\n')
    file.writelines(text)
    file.close()
#eventid datetime name mag magtype lat lon depth np1_strike np1_dip np1_rake
#file=open("evt_info.txt",'a+')
#text=(f'{0} {starttime} {'name'} {stala} {stalo} {stael} {stadp} {start} {end}\n')
#eventid datetime name mag magtype lat lon depth np1_strike np1_dip np1_rake
#file.writelines(text)
#file.close()
