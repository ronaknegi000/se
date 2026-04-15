import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sensors
import detector
import signal_control
import analytics


class TestSensors(unittest.TestCase):

    def test_read_sensor_keys(self):
        data = sensors.read_sensor("N")
        self.assertIn("direction", data)
        self.assertIn("vehicle_count", data)
        self.assertIn("timestamp", data)
        self.assertIn("event", data)

    def test_vehicle_count_range(self):
        for _ in range(20):
            data = sensors.read_sensor("N")
            self.assertGreaterEqual(data["vehicle_count"], 0)
            self.assertLessEqual(data["vehicle_count"], 100)

    def test_all_directions_returned(self):
        data = sensors.get_all_sensor_data()
        self.assertEqual(len(data), 4)
        dirs = [d["direction"] for d in data]
        self.assertIn("N", dirs)
        self.assertIn("S", dirs)
        self.assertIn("E", dirs)
        self.assertIn("W", dirs)


class TestDetector(unittest.TestCase):

    def test_low_density(self):
        self.assertEqual(detector.classify_density(10), "Low")

    def test_medium_density(self):
        self.assertEqual(detector.classify_density(35), "Medium")

    def test_high_density(self):
        self.assertEqual(detector.classify_density(75), "High")

    def test_boundary_low(self):
        self.assertEqual(detector.classify_density(20), "Low")

    def test_boundary_medium(self):
        self.assertEqual(detector.classify_density(21), "Medium")

    def test_boundary_high(self):
        self.assertEqual(detector.classify_density(51), "High")

    def test_analyze_output_keys(self):
        sample = [{"direction": "N", "vehicle_count": 30, "timestamp": "t", "event": "NORMAL"}]
        result = detector.analyze(sample)
        self.assertIn("density", result[0])

    def test_most_congested(self):
        data = [
            {"direction": "N", "vehicle_count": 20, "density": "Low"},
            {"direction": "S", "vehicle_count": 80, "density": "High"},
        ]
        self.assertEqual(detector.most_congested(data)["direction"], "S")


class TestSignalControl(unittest.TestCase):

    def setUp(self):
        signal_control.clear_emergency()

    def test_green_time_increases_with_density(self):
        low = signal_control.calculate_green_time("Low")
        mid = signal_control.calculate_green_time("Medium")
        high = signal_control.calculate_green_time("High")
        self.assertLess(low, mid)
        self.assertLess(mid, high)

    def test_min_green_respected(self):
        t = signal_control.calculate_green_time("Low")
        self.assertGreaterEqual(t, signal_control.MIN_GREEN)

    def test_generate_signals_keys(self):
        data = [
            {"direction": "N", "vehicle_count": 20, "density": "Low"},
            {"direction": "S", "vehicle_count": 40, "density": "Medium"},
            {"direction": "E", "vehicle_count": 60, "density": "High"},
            {"direction": "W", "vehicle_count": 10, "density": "Low"},
        ]
        signals = signal_control.generate_signals(data)
        self.assertIn("N", signals)
        self.assertIn("S", signals)

    def test_emergency_direction_gets_priority(self):
        signal_control.set_emergency("N")
        data = [
            {"direction": "N", "vehicle_count": 20, "density": "Low"},
            {"direction": "S", "vehicle_count": 40, "density": "Medium"},
            {"direction": "E", "vehicle_count": 60, "density": "High"},
            {"direction": "W", "vehicle_count": 10, "density": "Low"},
        ]
        signals = signal_control.generate_signals(data)
        self.assertEqual(signals["N"]["reason"], "EMERGENCY")
        self.assertEqual(signals["S"]["state"], "RED")


class TestAnalytics(unittest.TestCase):

    def test_init_log_creates_file(self):
        analytics.LOG_FILE = "test_traffic_log.csv"
        if os.path.exists(analytics.LOG_FILE):
            os.remove(analytics.LOG_FILE)
        analytics.init_log()
        self.assertTrue(os.path.exists(analytics.LOG_FILE))
        os.remove(analytics.LOG_FILE)

    def test_compute_stats_empty(self):
        analytics.LOG_FILE = "test_empty.csv"
        if os.path.exists(analytics.LOG_FILE):
            os.remove(analytics.LOG_FILE)
        stats = analytics.compute_stats()
        self.assertEqual(stats["total_cycles"], 0)
        os.remove(analytics.LOG_FILE)

    def tearDown(self):
        analytics.LOG_FILE = "traffic_log.csv"


if __name__ == "__main__":
    unittest.main(verbosity=2)
