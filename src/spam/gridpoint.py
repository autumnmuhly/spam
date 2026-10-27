from .mesh_setup import latlon_cartesian,cart_latlon
from .distaz import DistAz

class Location:
    def __init__(self,lat,lon,cart=None):
        "Location is made up of a lat, lon and cartesian coordinates"
        self.lat=lat
        self.lon=lon
        self._cart=cart
    @property
    def cart(self):
        if self._cart is None:
            self._cart=latlon_cartesian(self.lat,self.lon)
        return self._cart 
    def distTo(self, loc):
        return DistAz(self.lat,self.lon,loc.lat,loc.lon)
    def __str__(self):
        return f"{self.lat},{self.lon}"

class Cartesian:
    def __init__(self,cart):
        "cartesian coordinates (x,y,z)"
        self.cart=cart
        self.x,self.y,self.z= cart

class Gridpoint:
    def __init__(self,cart):
        "grid point takes in a cartesian touple but also has a lat and lon"
        com=Cartesian(cart)
        lat,lon=cart_latlon(com.x,com.y,com.z)
        self.loc=Location(lat,lon,cart)
        self.phaseCount = {}
    def to_json(self):
        return {
            "lat": self.loc.lat,
            "lon": self.loc.lon,
            "x": self.loc.cart[0],
            "y": self.loc.cart[1],
            "z": self.loc.cart[2]
        }
    @classmethod
    def from_json(cls, jsonObj):
        cart = (jsonObj["x"], jsonObj["y"], jsonObj["z"])
        return cls(cart)
    def distToSta(self, sta):
        return self.loc.distTo(sta.loc)
    def __str__(self):
        return f"gp {self.loc}"

class Station:
    def __init__(self,netwrk,name,loc,start,stop,locCode):
        "station takes a location, start time, and end time"
        self.name=name
        self.netwrk=netwrk
        self.loc=loc
        self.start=start
        self.stop=stop
        self.locCode=locCode
    def to_json(self):
        return {
            "name":self.name,
            "locCode":self.locCode,
            "netwrk":self.netwrk,
            "loc":{
                "lat":self.loc.lat,
                "lon":self.loc.lon
                },
            "start":self.start.isoformat(),
            "stop":self.stop.isoformat()
                }
    @classmethod
    def from_json(cls,jsonObj):
        locCode=jsonObj['locCode']
        netwrk=jsonObj['netwrk']
        name=jsonObj['name']
        loc=Location(jsonObj["loc"]["lat"],lon=jsonObj["loc"]["lon"])
        start=jsonObj['start']
        stop=jsonObj['stop']
        return cls(netwrk,name,loc,start,stop,locCode)
    def __str__(self):
        return f"{self.netwrk}_{self.name} {self.loc}"

class EQ:
    def __init__(self,loc,depth,event_time):
        'earthquakes have a location and a time'
        self.loc=loc
        self.depth=depth
        self.time=event_time
    def to_json(self):
        return {
            "loc":{
                "lat":self.loc.lat,
                "lon":self.loc.lon
                },
            "time":self.time.isoformat(),
            "depth":self.depth
            }
    @classmethod
    def from_json(cls,jsonObj):
        depth=jsonObj['depth']
        event_time=jsonObj['time']
        loc=Location(jsonObj["loc"]["lat"],lon=jsonObj["loc"]["lon"])
        return cls(loc,depth,event_time)
    def __str__(self):
        return f"{self.time} {self.loc}"


class MetaData:
    def __init__(self,version,datecreated):
        "Data has a version and a date it was created on"
        self.version=version
        self.datecreated=datecreated
    def to_json(self):
        return {
            "datecreated":self.datecreated,
            "version":self.version,
        }
    @classmethod
    def from_json(cls,jsonObj):
        version=jsonObj['version']
        datecreated=jsonObj['datecreated']
        return cls(version,datecreated)