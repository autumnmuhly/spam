#create sta list for spam. out put is sta_info.txt
import obspy
from obspy.clients.fdsn import Client
from obspy.core.utcdatetime import UTCDateTime
import os
from datetime import datetime

client=Client("IRIS")
starttime=UTCDateTime("2006-11-13")
endtime=UTCDateTime("2024-11-27")
inventory=client.get_stations(starttime=starttime, endtime=endtime)

for network_list in inventory:
    network=network_list.code
    for station in network_list:
        sta=station.code
        stala=format(station.latitude,'.4f')
        stalo=format(station.longitude,'.4f')
        stael=station.elevation
        stadp=0.0
        location=0.0
        start=UTCDateTime(station.start_date).strftime("%Y-%m-%dT%H:%M:%S")
        try:
            end=UTCDateTime(station.end_date).strftime("%Y-%m-%dT%H:%M:%S")
        except:
            end=datetime.now()
            end=UTCDateTime(end).strftime("%Y-%m-%dT%H:%M:%S")
        file=open("sta_info.txt",'a+')
        text=(f'{network} {sta} {location} {stala} {stalo} {stael} {stadp} {start} {end}\n')
        file.writelines(text)
        file.close()
