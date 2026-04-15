# Smart Traffic Management System — Full Documentation
## Software Requirements Specification (SRS) + Diagrams + Test Cases + Viva Guide

---

# PART 1: SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for a simulation-based Smart Traffic Management
System. The system uses Python to simulate IoT sensor data, classify traffic density,
control traffic signals adaptively, and present results through a real-time web dashboard.

### 1.2 Scope
The system handles:
- Simulating vehicle counts for 4 intersection directions (N, S, E, W)
- Classifying traffic density using rule-based logic
- Dynamically assigning green signal times based on congestion
- Emergency vehicle override capability
- Logging data to CSV and computing analytics
- Displaying everything on a Flask-based web dashboard

### 1.3 Definitions
| Term         | Meaning                                      |
|-------------|----------------------------------------------|
| IoT Sensor  | Simulated Python function mimicking real sensors |
| Density     | Traffic level: Low / Medium / High           |
| Green Time  | Duration a signal stays green (in seconds)  |
| Rush Hour   | Peak traffic period: 7–9 AM and 5–7 PM      |
| Emergency   | High-priority vehicle override mode          |

---

## 2. Overall Description

### 2.1 System Architecture
```
IoT Sensors (sensors.py)
        |
        v
Vehicle Detector (detector.py)
        |
        v
Signal Controller (signal_control.py)
        |
        v
Analytics Logger (analytics.py)
        |
        v
Flask Dashboard (app.py + templates/index.html)
```

### 2.2 Assumptions
- System runs locally; no actual hardware required
- Time-based logic uses the server's system clock
- Traffic data refreshes every 3 seconds on the dashboard

---

## 3. Functional Requirements

| ID   | Requirement                                                                 |
|------|-----------------------------------------------------------------------------|
| FR-1 | System SHALL simulate vehicle counts for 4 directions every cycle           |
| FR-2 | System SHALL vary vehicle counts based on time of day (rush hour logic)     |
| FR-3 | System SHALL randomly simulate accident events (~5% probability)            |
| FR-4 | System SHALL classify traffic as Low / Medium / High                        |
| FR-5 | System SHALL assign green time proportional to traffic density              |
| FR-6 | System SHALL guarantee minimum green time (10 seconds) to prevent starvation|
| FR-7 | System SHALL support emergency vehicle override for any direction            |
| FR-8 | System SHALL log each cycle to a CSV file                                   |
| FR-9 | System SHALL compute average green time and most congested direction        |
| FR-10| System SHALL display real-time data and charts on a web dashboard           |

---

## 4. Non-Functional Requirements

| ID    | Requirement                                               |
|-------|-----------------------------------------------------------|
| NFR-1 | Dashboard SHALL refresh without full page reload (AJAX)  |
| NFR-2 | System SHALL be modular — each concern in its own file   |
| NFR-3 | Code SHALL be readable and maintainable by a junior dev  |
| NFR-4 | Log file SHALL persist across server restarts            |

---

## 5. System Constraints
- Python 3.8+ required
- Flask is the only external dependency
- No database; CSV is used for storage

---

# PART 2: ER DIAGRAM (Textual Representation)

```
+------------------+        +--------------------+        +-------------------+
|   TrafficReading |        |   SignalDecision    |        |   TrafficLog      |
+------------------+        +--------------------+        +-------------------+
| direction (PK)   |------->| direction (FK)     |------->| id (auto)         |
| vehicle_count    |        | green_time         |        | timestamp         |
| timestamp        |        | state              |        | direction         |
| event            |        | reason             |        | vehicle_count     |
+------------------+        +--------------------+        | density           |
                                                           | green_time        |
                                                           | event             |
                                                           +-------------------+
```

**Relationships:**
- One TrafficReading → produces → One SignalDecision (1:1 per direction per cycle)
- One cycle (4 TrafficReadings) → logged as → 4 TrafficLog rows

---

# PART 3: CLASS DIAGRAM

```
+=======================+
|       Sensor          |
+=======================+
| DIRECTIONS: list      |
| RUSH_HOURS: list      |
+-----------------------+
| is_rush_hour(h)       |
| base_vehicle_count(h) |
| simulate_accident()   |
| read_sensor(dir)      |
| get_all_sensor_data() |
+=======================+

+=======================+
|      Detector         |
+=======================+
| LOW_MAX = 20          |
| MED_MAX = 50          |
+-----------------------+
| classify_density(c)   |
| analyze(sensor_data)  |
| most_congested(data)  |
+=======================+

+=======================+
|    SignalControl      |
+=======================+
| MIN_GREEN = 10        |
| MAX_GREEN = 60        |
| EMERGENCY_GREEN = 90  |
| emergency_direction   |
+-----------------------+
| set_emergency(dir)    |
| clear_emergency()     |
| calculate_green_time()|
| generate_signals(data)|
+=======================+

+=======================+
|      Analytics        |
+=======================+
| LOG_FILE: str         |
| HEADERS: list         |
+-----------------------+
| init_log()            |
| log_cycle(data, sigs) |
| compute_stats()       |
| get_recent_logs(n)    |
+=======================+

+=======================+
|      FlaskApp         |
+=======================+
| app: Flask            |
+-----------------------+
| index()               |
| traffic_data()        |
| trigger_emergency(d)  |
| clear_emergency()     |
| logs()                |
+=======================+

Dependency arrows:
FlaskApp ──uses──> Sensor, Detector, SignalControl, Analytics
Detector ──uses──> (output of Sensor)
SignalControl ──uses──> (output of Detector)
Analytics ──uses──> (output of Detector + SignalControl)
```

---

# PART 4: DATA FLOW DIAGRAM (Level 1)

```
[System Clock] ──> [Sensor Module] ──> raw_data[]
                                           |
                                           v
                              [Detector Module] ──> analyzed_data[]
                                           |
                                           v
                       [Signal Control Module] ──> signals{}
                                           |
                                           v
                           [Analytics Module] ──> CSV log + stats
                                           |
                                           v
                           [Flask Dashboard] ──> JSON API + Web UI
                                           |
                                           v
                                    [Browser/User]
```

---

# PART 5: TEST CASES

## Module: sensors.py

| TC-ID  | Test Description                        | Input          | Expected Output                   | Status |
|--------|-----------------------------------------|----------------|-----------------------------------|--------|
| TC-S01 | read_sensor returns required keys       | dir = "N"      | dict with direction, count, etc.  | PASS   |
| TC-S02 | vehicle_count within 0–100              | dir = "E"      | 0 <= count <= 100                 | PASS   |
| TC-S03 | get_all_sensor_data returns 4 entries   | None           | list of 4 dicts                   | PASS   |
| TC-S04 | All 4 directions present in output      | None           | [N, S, E, W] in list              | PASS   |

## Module: detector.py

| TC-ID  | Test Description                        | Input          | Expected Output | Status |
|--------|-----------------------------------------|----------------|-----------------|--------|
| TC-D01 | Count 10 → Low density                 | 10             | "Low"           | PASS   |
| TC-D02 | Count 35 → Medium density              | 35             | "Medium"        | PASS   |
| TC-D03 | Count 75 → High density                | 75             | "High"          | PASS   |
| TC-D04 | Boundary: 20 → Low                     | 20             | "Low"           | PASS   |
| TC-D05 | Boundary: 21 → Medium                  | 21             | "Medium"        | PASS   |
| TC-D06 | most_congested returns correct dir      | mixed data     | dir with max    | PASS   |

## Module: signal_control.py

| TC-ID  | Test Description                         | Input          | Expected Output                   | Status |
|--------|------------------------------------------|----------------|-----------------------------------|--------|
| TC-SC01| High density gets more time than Low     | High, Low      | high_time > low_time              | PASS   |
| TC-SC02| Minimum green time always respected      | Low density    | green_time >= 10                  | PASS   |
| TC-SC03| Emergency direction gets 90s             | emergency = N  | signals["N"]["green_time"] == 90  | PASS   |
| TC-SC04| Other dirs go RED during emergency       | emergency = N  | signals["S"]["state"] == "RED"    | PASS   |
| TC-SC05| All 4 directions have signal entry       | 4-dir data     | len(signals) == 4                 | PASS   |

## Module: analytics.py

| TC-ID  | Test Description                         | Input          | Expected Output                   | Status |
|--------|------------------------------------------|----------------|-----------------------------------|--------|
| TC-A01 | init_log creates CSV if missing          | No file        | file created with header          | PASS   |
| TC-A02 | compute_stats on empty file → 0 cycles   | empty CSV      | total_cycles == 0                 | PASS   |
| TC-A03 | log_cycle writes 4 rows per cycle        | 4-dir data     | CSV rows increase by 4            | PASS   |

---

# PART 6: MAINTENANCE PLAN

## 6.1 Regular Maintenance Tasks

| Task                        | Frequency  | Action                                      |
|-----------------------------|------------|---------------------------------------------|
| Clear traffic_log.csv       | Weekly     | Archive or delete old CSV logs              |
| Review rush hour settings   | Monthly    | Update RUSH_HOURS in sensors.py as needed   |
| Check density thresholds    | Monthly    | Tune LOW_MAX, MED_MAX in detector.py        |
| Update green time limits    | Quarterly  | Adjust MIN_GREEN, MAX_GREEN in signal_control.py |

## 6.2 Corrective Maintenance
- If dashboard doesn't update: check Flask server is running on port 5000
- If CSV grows too large: add log rotation in analytics.py
- If signals seem unfair: adjust DENSITY_WEIGHTS in signal_control.py

## 6.3 Scaling / Enhancement Roadmap
| Enhancement             | Module to Modify         | Effort  |
|-------------------------|--------------------------|---------|
| Add more intersections  | sensors.py, app.py       | Medium  |
| Use real time from DB   | analytics.py             | Medium  |
| Add ML-based prediction | New: predictor.py        | High    |
| Use SQLite instead of CSV | analytics.py            | Low     |
| Add user auth to dashboard | app.py + templates    | Low     |

---

# PART 7: HOW TO RUN THE PROJECT

## Step 1: Prerequisites
Ensure Python 3.8+ is installed:
```bash
python --version
```

## Step 2: Install Dependencies
```bash
cd smart_traffic
pip install -r requirements.txt
```

## Step 3: Run the Application
```bash
python app.py
```

## Step 4: Open Dashboard
Open your browser and go to:
```
http://127.0.0.1:5000
```

## Step 5: Run Tests
In a separate terminal:
```bash
python tests.py
```

## Step 6: Explore Emergency Feature
Click any "🚨 North / South / East / West" button on the dashboard to trigger emergency
override. Click "✕ Clear" to restore normal operation.

---

# PART 8: MODULE EXPLANATIONS (Simple Words)

### sensors.py — "The Road Cameras"
This file pretends to be IoT sensors installed at a traffic intersection. It generates
random vehicle counts, makes them higher during morning and evening rush hours, and
occasionally simulates an accident that causes a spike in traffic.

### detector.py — "The Traffic Analyst"
Takes the raw numbers from sensors and puts them into three buckets: Low (quiet road),
Medium (normal traffic), High (jam). Also finds which direction is most congested.

### signal_control.py — "The Traffic Police"
Decides how long each traffic light should stay green. Busier lanes get more time,
quiet lanes still get a minimum so they're never ignored. If an ambulance or fire
truck is detected, it overrides everything and gives that direction a long green light.

### analytics.py — "The Record Keeper"
Saves every traffic cycle into a CSV file (like an Excel sheet). Later calculates the
average green time and which direction has historically been most congested.

### app.py — "The Control Room"
A Flask web server that connects all the modules together and serves data to the
browser via simple API endpoints (/api/traffic, /api/logs, etc.).

### templates/index.html — "The Dashboard Screen"
The visual interface. Shows the intersection, traffic counts, signal states, a live
chart that updates every 3 seconds, and buttons to trigger emergency mode.

---

# PART 9: VIVA QUESTIONS & ANSWERS

**Q1: What is the purpose of this project?**
A: To simulate a smart traffic management system that uses IoT-like sensors to collect
traffic data, classify congestion levels, adaptively control signal timings, and provide
a real-time monitoring dashboard — all in pure Python.

**Q2: How do you simulate IoT sensors in software?**
A: Using Python's `random` module with rule-based logic. The function generates higher
counts during rush hours (7–9 AM, 5–7 PM) and lower counts at night. A 5% random chance
simulates an accident event. This mimics how a real inductive loop or camera-based sensor
would report varying vehicle counts.

**Q3: What is adaptive traffic signal control?**
A: Instead of fixed green durations (e.g., always 30 seconds), the system assigns green
time proportionally based on traffic density. A High-density lane gets more time, a Low
lane gets less but always at least the minimum (10 seconds) to prevent starvation.

**Q4: What is lane starvation and how do you prevent it?**
A: Lane starvation happens when one direction never gets a green signal because other
directions always have more traffic. We prevent it by enforcing a MIN_GREEN of 10 seconds
for every direction, regardless of its density level.

**Q5: Explain the emergency vehicle logic.**
A: When an emergency is triggered for a direction (e.g., North), that direction gets
90 seconds of green and all others switch to RED. This simulates how real intersections
give priority to ambulances or fire trucks using IR sensors.

**Q6: Why did you choose CSV instead of a database?**
A: For simplicity and zero external dependencies. CSV is readable, easy to inspect, and
sufficient for this simulation scale. In a production system, we'd use SQLite or PostgreSQL.

**Q7: What is Flask and why is it used here?**
A: Flask is a lightweight Python web framework. We use it to serve the dashboard HTML
and create REST API endpoints (/api/traffic, /api/logs) that the browser polls every
3 seconds using JavaScript fetch calls.

**Q8: What design pattern does the project follow?**
A: A layered/pipeline architecture: Sensor Layer → Detection Layer → Control Layer →
Analytics Layer → Presentation Layer. Each layer depends only on the layer above it,
making it easy to replace or test any one module independently.

**Q9: How would you add a real IoT sensor to this system?**
A: Replace the `read_sensor()` function in sensors.py with an HTTP call to a real sensor
API (or read from an MQTT broker). The rest of the pipeline — detector, signal control,
analytics — would work unchanged because they consume the same data format.

**Q10: What are the limitations of this simulation?**
A: (1) It uses random numbers instead of real sensor data. (2) It has a single intersection.
(3) Signal timing doesn't account for vehicle queues across cycles. (4) No real-time
coordination with adjacent intersections. These are valid future improvements.

**Q11: How does the Chart.js chart work in the dashboard?**
A: Every 3 seconds, JavaScript fetches /api/traffic, extracts vehicle counts for N/S/E/W,
appends them to 4 line chart datasets, and removes the oldest point to create a
scrolling time-series effect. Chart.js handles the rendering.

**Q12: What is the time complexity of generate_signals()?**
A: O(n) where n is the number of directions (always 4 in this case). It iterates once
through the analyzed_data list to compute weights and assign green times. Effectively O(1)
for fixed directions.

---

# PART 10: FOLDER STRUCTURE

```
smart_traffic/
│
├── app.py                  ← Flask server + API routes
├── sensors.py              ← IoT sensor simulation
├── detector.py             ← Density classification
├── signal_control.py       ← Adaptive signal timing + emergency
├── analytics.py            ← CSV logging + statistics
├── tests.py                ← Unit tests for all modules
├── requirements.txt        ← Flask dependency
├── traffic_log.csv         ← Auto-created when app runs
│
└── templates/
    └── index.html          ← Real-time web dashboard
```
