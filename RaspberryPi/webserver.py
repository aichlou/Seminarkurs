from flask import Flask, request, jsonify, render_template
import logging
import state

# Globale Zustände (z.B. Sensoren oder Motoren)
states = [False, False, False, False, False, False, False]


def set_state(index, value):
    """Ändert einen State an der gegebenen Position"""
    global states
    if isinstance(index, int) and 0 <= index < len(states):
        states[index] = bool(value)


def get_states():
    """Gibt alle States zurück"""
    return list(states)


def host_server(commands):
    app = Flask(__name__)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route("/action", methods=["POST"])
    def action():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Ungültige Anfrage"}), 400

        axis = data.get("axis")
        speed = data.get("speed")
        active = data.get("active")

        if axis not in ("X", "Y", "Z"):
            return jsonify({"error": "Ungültige Achse"}), 400
        if not isinstance(active, bool):
            return jsonify({"error": "Ungültiger Aktivitätswert"}), 400

        if active:
            try:
                commands.put(("start_motor", axis, float(speed)))
            except (TypeError, ValueError):
                return jsonify({"error": "Ungültige Geschwindigkeit"}), 400
        else:
            commands.put(("stop_motor", axis))

        return jsonify({"ok": True}), 200

    @app.route("/status")
    def status():
        return jsonify(get_states())

    @app.route("/init", methods=["GET"])
    def initialize():
        print("INIT WURDE GEDRÜCKT")
        if not state.was_init:
            print("STARTE INIT VON WEBSERVER AUS")
            commands.put(("init",))
            state.was_init = True
            return jsonify({"ok": True}), 200
        print("System ist bereits initialisiert")
        return jsonify({"error": "Bereits initialisiert"}), 409

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
