
from multiprocessing import Pool
import functools
import os
from .mesh_setup import latlon_cartesian,cart_latlon
from .distaz import DistAz
from .arrConfig import calcArthCenter
from .gridpoint import Gridpoint,Station,EQ

def is_ok_eq_sta(evt,sta,distRange):
    "Takes in an eq and checks if sta/pt is existed at time of event and if the stations are within range"
    min_dist=distRange[0]
    max_dist=distRange[1]
    if sta.start<=evt.time and (sta.stop=='None' or evt.time<=sta.stop):
        dist=DistAz(evt.loc.lat,evt.loc.lon,sta.loc.lat,sta.loc.lon)
        gc=abs(dist.delta)
        if min_dist<gc<max_dist:
            return True
    return False

def calcBasestation(array):
    "Takes in a list of stations, finds the most arthimetic center and calculates what station is closest"
    # calcArthCenter(array)
    # print(f'this is array center {array.center}')
    closest_dist=400
    for sta in array.good_sta_list:
        dist=DistAz(array.center.lat,array.center.lon,sta.loc.lon,sta.loc.lat)
        dist_sta_cent=dist.delta
        if dist_sta_cent< closest_dist:
            closest_dist=dist.delta
            array.basestation=sta

def is_array_gp_okay(arr,spacing):
    x=0
    y=0
    z=0
    for sta in arr.sta_list:
        cart=latlon_cartesian(sta.loc.lat,sta.loc.lon)
        #print(cart.x,cart.y,cart.z)
        x+=cart.x
        y+=cart.y
        z+=cart.z
    num=len(arr.sta_list)
    cm_latlon=cart_latlon(x/num,y/num,z/num)
    diff=DistAz(arr.pt.loc.lat,arr.pt.loc.lon,cm_latlon[0],cm_latlon[1])
    if diff.delta>=(spacing/2):
        return False
    return True


class EqtoArrayList:
    "a list of arrays for all the earthquakes"
    def __init__(self,evt):
        self.evt=evt 
        self.array_list=[]
    def check_array(self,arr,distRange,minSta):
        "checks if any arrays are within range from earthquake, if so add array to the array list"
        min=distRange[0]
        max=distRange[1]
        dist=DistAz(arr.array.pt.loc.lat,arr.array.pt.loc.lon,self.evt.loc.lat,self.evt.loc.lon)
        distance=abs(dist.delta)
        is_ok = False
        if distance>min and distance<max:
            sta_count=0
            for sta in arr.array.sta_list:
                if is_ok_eq_sta(self.evt,sta,distRange) == True:
                    sta_count+=1
                    if sta_count >= minSta:
                        self.array_list.append(arr)
                        is_ok = True
                        break
        return is_ok
    @property
    def array_count(self):
        return len(self.array_list)

class ArrayToEqlist:
    "a list of eq for all arrrays"
    def __init__(self,array):
        self.array=array
        self.eqlists=[]
        self.eqcount=len(self.eqlists)
        self.good_sta_list=[]
    def to_json(self):
        return {
            "array":self.array.to_json(),
            "eqlists":[eq.to_json() for eq in self.eqlists],
            "eqcount":self.eqcount,
            "good_sta_list":[sta.to_json() for sta in self.good_sta_list]
            }
    @classmethod
    def from_json(cls,jsonObj):
        array=Array.from_json(jsonObj["array"])
        obj=cls(array)
        obj.eqcount=jsonObj["eqcount"]
        obj.eqlists=[EQ.from_json(eq) for eq in jsonObj["eqlists"]]
        obj.good_sta_list=[Station.from_json(sta) for sta in jsonObj["good_sta_list"]]
        return obj
    def check_eq(self,evt,distRange,minSta):
        "checks if any events are within range from array, if so count 1 for that array and add event to eqlist"
        min=distRange[0]
        max=distRange[1]
        dist=DistAz(self.array.pt.loc.lat,self.array.pt.loc.lon,evt.loc.lat,evt.loc.lon)
        distance=abs(dist.delta)
        if distance>min and distance<max:
            self.truth_count=0
            counted_eq = False
            for sta in self.array.sta_list:
                if is_ok_eq_sta(evt,sta,distRange) == True:
                    self.good_sta_list.append(sta)
                    self.truth_count+=1
                    if self.truth_count >= minSta and not counted_eq:
                        self.eqcount +=1 #is now adding one to the grid point if all stations meet the criteria
                        self.eqlists.append(evt)
                        counted_eq = True
        return True

class Array:
    def __init__(self,pt,radius, station_distances, basestation=None):
        "an array has a grid point, a radius, a list of stations in it, and a base station"
        self.pt=pt
        self.radius=radius
        self.sta_list=list(station_distances) 
        self.eqcount=0
        self.sta_array_list=[]
        self.basestation=basestation
        self.station_distances=station_distances
    def to_json(self):
        return {
                "pt": self.pt.to_json(),
                "radius": self.radius,
                "sta_array_list":[sta.to_json() for sta in self.sta_array_list],
                "eqcount":self.eqcount,
                "basestation":(self.basestation.to_json() if self.basestation else None),
                "station_distances":[
                    {
                        "station":sta.to_json(),
                        "distance":dist
                    }
                    for sta,dist in self.station_distances.items()
                ]
                }
    @classmethod
    def from_json(cls, jsonObj):
        pt = Gridpoint.from_json(jsonObj["pt"])
        station_distances={Station.from_json(item["station"]): item["distance"] for item in jsonObj["station_distances"]}
        basesta_name=jsonObj.get('basestation')
        basestation=(Station.from_json(basesta_name) if basesta_name else None)
        array = cls(pt, jsonObj["radius"], station_distances,basestation)
        array.eqcount=jsonObj.get("eqcount",0)
        array.sta_array_list=[Station.from_json(sta) for sta in jsonObj.get("sta_array_list",[])]
        return array

def form_array(sta_list,pt,radius):
    sta_array_list=[]
    sta_dist = {}
    min_dist=361
    for sta in sta_list:
        dist=DistAz(pt.loc.lat,pt.loc.lon,sta.loc.lat,sta.loc.lon)
        pt_sta=abs(dist.delta)
        if pt_sta<=radius:
            sta_array_list.append(sta)
            sta_dist[sta] = pt_sta
            if pt_sta<min_dist:
                min_dist=pt_sta
    return Array(pt,radius,sta_dist)


def inner_form_array(sta_list, radius, pt):
    return form_array(sta_list,pt,radius)

def form_all_array(sta_list,grid_array,radius,minSta):
    array_list=[]
    partial_form_array = functools.partial(inner_form_array, sta_list, radius)

    with Pool(processes=(os.process_cpu_count()-1)) as pool:
        array_list = pool.map(partial_form_array, grid_array)

    return [a for a in array_list if len(a.sta_list)>=minSta]

class EqGridAssignment:
    def __init__(self,gridpoint,earthquake):
        self.gridpoint=gridpoint
        self.eqList=earthquake

def form_eq(evt_list,pt,radius):
    "each earthquake is assigned to a gridpoint"
    eq_pt_list=[]
    for evt in evt_list:
        dist=DistAz(pt.loc.lat,pt.loc.lon,evt.loc.lat,evt.loc.lon)
        pt_evt=abs(dist.delta)
        if pt_evt<=radius:
            eq_pt_list.append(evt)
    return EqGridAssignment(pt,radius,eq_pt_list)

def form_all_eq_grid(evt_list,grid_array,radius):
    evt_pt_list=[]
    for pt in grid_array:
        evt_pt_list.append(form_eq(evt_list,pt,radius))
    return evt_pt_list
# create a class of earthquake array pairs for each earthquake

def items_in_dist(locList,point,minRadius,maxRadius):
    """""
    locList-list of things that have location 
    point- central location (a grid point)
    radius - distance radius around point
    """""
    good_locs = []
    for locItem in locList:
        dist = DistAz(locItem.loc.lat,locItem.loc.lon, point.loc.lat,point.loc.lon)
        dist=abs(dist.delta)
        if minRadius <= dist <= maxRadius:
            good_locs.append(locItem)
    return good_locs

