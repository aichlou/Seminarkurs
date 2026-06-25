from flask import Flask, request, jsonify, send_file, render_template
import logging

# Globale Zustände (z.B. Sensoren oder Motoren)
states = [False, False, False, False]
wasInit = False

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
    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    @app.route("/")
    def index():
        return render_template('index.html')

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
    
    @app.route("/init")
    def initialize():
        global wasInit
        if wasInit == False:
            commands.put(("init", ))
            wasInit = True
            return jsonify({"ok": True})
        else:
            return jsonify({"409": False})
    
    

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
