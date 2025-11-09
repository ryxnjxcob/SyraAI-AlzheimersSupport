from datetime import datetime
from .geo import haversine_m

def speed_kmh(lat1,lng1,t1,lat2,lng2,t2):
    if not t1 or not t2:
        return None
    dt = (t2 - t1).total_seconds()
    if dt <= 0:
        return None
    dist_m = haversine_m(lat1,lng1,lat2,lng2)
    kmh = (dist_m/1000.0) / (dt/3600.0)
    return kmh
