from flask import Flask, request, jsonify, send_file

# Globale Zustände (z.B. Sensoren oder Motoren)
states = [False, False, False, False]

def set_state(index, value):
    """Ändert einen State an der gegebenen Position"""
    global states
    if 0 <= index < len(states):
        states[index] = value

def get_states():
    """Gibt alle States zurück"""
    return states

def host_server(commands):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return send_file("index.html")

    @app.route("/action", methods=["POST"])
    def action():
        print("Button wurde gedrückt!")
        data = request.json
        axis = data["axis"]
        speed = data["speed"]
        active = data["active"]
        if active:
            commands.put(("start_motor", axis, speed))
        else:
            commands.put(("stop_motor", axis))
        return jsonify({"ok": True})

    @app.route("/status")
    def status():
        return jsonify(get_states())
    
    @app.route("/initialize")
    def initialize():
        commands.put(("initialize", ))
        return jsonify({"ok": True})

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)