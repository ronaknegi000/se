from flask import Flask, jsonify, render_template
import sensors, detector, signal_control, analytics

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/traffic")
def traffic_data():
    raw = sensors.get_all_sensor_data()
    analyzed = detector.analyze(raw)
    signals = signal_control.generate_signals(analyzed)
    analytics.log_cycle(analyzed, signals)
    stats = analytics.compute_stats()

    return jsonify({
        "traffic": analyzed,
        "signals": signals,
        "stats": stats
    })

@app.route("/api/emergency/<direction>")
def trigger_emergency(direction):
    direction = direction.upper()
    if direction in ["N", "S", "E", "W"]:
        signal_control.set_emergency(direction)
        return jsonify({"status": f"Emergency set for {direction}"})
    return jsonify({"error": "Invalid direction"}), 400

@app.route("/api/emergency/clear")
def clear_emergency():
    signal_control.clear_emergency()
    return jsonify({"status": "Emergency cleared"})

@app.route("/api/logs")
def logs():
    return jsonify(analytics.get_recent_logs())

if __name__ == "__main__":
    import threading, webbrowser
    analytics.init_log()
    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    if __name__ == "__main__":
     app.run()
