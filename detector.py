def classify_density(vehicle_count):
    if vehicle_count <= 20:
        return "Low"
    elif vehicle_count <= 50:
        return "Medium"
    else:
        return "High"

def analyze(sensor_data):
    result = []
    for reading in sensor_data:
        density = classify_density(reading["vehicle_count"])
        result.append({
            "direction": reading["direction"],
            "vehicle_count": reading["vehicle_count"],
            "density": density,
            "timestamp": reading["timestamp"],
            "event": reading["event"]
        })
    return result

def most_congested(analyzed_data):
    return max(analyzed_data, key=lambda x: x["vehicle_count"])