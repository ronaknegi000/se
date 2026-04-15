import random
import datetime

DIRECTIONS = ["N", "S", "E", "W"]

RUSH_HOURS = [(7, 9), (17, 19)]

def is_rush_hour(hour):
    return any(start <= hour < end for start, end in RUSH_HOURS)

def base_vehicle_count(hour):
    if is_rush_hour(hour):
        return random.randint(40, 80)
    elif 22 <= hour or hour < 6:
        return random.randint(2, 15)
    else:
        return random.randint(15, 40)

def simulate_accident():
    return random.random() < 0.05

def read_sensor(direction):
    hour = datetime.datetime.now().hour
    count = base_vehicle_count(hour)

    if simulate_accident():
        count = min(count + random.randint(20, 40), 100)
        event = "ACCIDENT"
    else:
        event = "NORMAL"

    return {
        "direction": direction,
        "vehicle_count": count,
        "timestamp": datetime.datetime.now().isoformat(),
        "event": event
    }

def get_all_sensor_data():
    return [read_sensor(d) for d in DIRECTIONS]