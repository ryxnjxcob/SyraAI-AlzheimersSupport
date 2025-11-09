from typing import List, Tuple, Optional
from datetime import datetime
from .utils import speed_kmh

# Simple heuristic: flag if instantaneous speed exceeds threshold (e.g., 12 km/h walking unlikely) 
# or if big deviation in short time. Placeholder for IsolationForest / LSTM later.

def simple_anomaly_flag(locations: List[Tuple[float, float, datetime]], speed_threshold_kmh: float = 12.0) -> bool:
    if len(locations) < 2:
        return False
    (lat1, lng1, t1), (lat2, lng2, t2) = locations[-2], locations[-1]
    spd = speed_kmh(lat1, lng1, t1, lat2, lng2, t2)
    return spd is not None and spd > speed_threshold_kmh
