import time

MIN_GREEN = 10
MAX_GREEN = 60
EMERGENCY_GREEN = 90

DENSITY_WEIGHTS = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}

# Opposite pairs: when N/S are green, E/W are red — and vice versa
OPPOSITE_PAIRS = [["N", "S"], ["E", "W"]]

emergency_direction = None
_cycle_start = time.time()
_active_pair_index = 0
_pair_durations = [MIN_GREEN, MIN_GREEN]

def set_emergency(direction):
    global emergency_direction
    emergency_direction = direction

def clear_emergency():
    global emergency_direction
    emergency_direction = None

def calculate_green_time(density):
    weight = DENSITY_WEIGHTS[density]
    total_weights = sum(DENSITY_WEIGHTS.values())
    fraction = weight / total_weights
    return int(MIN_GREEN + fraction * (MAX_GREEN - MIN_GREEN))

def _get_pair_green_time(pair_dirs, analyzed_data):
    counts = {item["direction"]: item for item in analyzed_data}
    densities = [counts[d]["density"] for d in pair_dirs if d in counts]
    if not densities:
        return MIN_GREEN
    best = max(densities, key=lambda d: DENSITY_WEIGHTS[d])
    return calculate_green_time(best)

def generate_signals(analyzed_data):
    global emergency_direction, _cycle_start, _active_pair_index, _pair_durations

    directions = [d["direction"] for d in analyzed_data]
    signals = {}

    if emergency_direction and emergency_direction in directions:
        for item in analyzed_data:
            if item["direction"] == emergency_direction:
                signals[item["direction"]] = {
                    "state": "GREEN",
                    "green_time": EMERGENCY_GREEN,
                    "reason": "EMERGENCY"
                }
            else:
                signals[item["direction"]] = {
                    "state": "RED",
                    "green_time": 0,
                    "reason": "EMERGENCY_HOLD"
                }
        return signals

    # Recalculate durations for both pairs each cycle
    _pair_durations = [
        _get_pair_green_time(OPPOSITE_PAIRS[0], analyzed_data),
        _get_pair_green_time(OPPOSITE_PAIRS[1], analyzed_data),
    ]

    # Check if current active pair's green time has elapsed → switch pair
    elapsed = time.time() - _cycle_start
    if elapsed >= _pair_durations[_active_pair_index]:
        _active_pair_index = 1 - _active_pair_index   # toggle 0 ↔ 1
        _cycle_start = time.time()

    green_pair = OPPOSITE_PAIRS[_active_pair_index]
    red_pair   = OPPOSITE_PAIRS[1 - _active_pair_index]
    remaining  = max(0, int(_pair_durations[_active_pair_index] - (time.time() - _cycle_start)))

    density_map = {item["direction"]: item["density"] for item in analyzed_data}

    for d in green_pair:
        signals[d] = {
            "state": "GREEN",
            "green_time": remaining,
            "reason": density_map.get(d, "Low")
        }

    next_green = int(_pair_durations[1 - _active_pair_index])
    for d in red_pair:
        signals[d] = {
            "state": "RED",
            "green_time": next_green,
            "reason": density_map.get(d, "Low")
        }

    return signals
