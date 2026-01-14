from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Beispiel-Zustände (z.B. Sensoren oder Motoren)
states = [False, True, False, True]

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/action", methods=["POST"])
def action():
    print("Button wurde gedrückt!")
    return jsonify({"ok": True})

@app.route("/status")
def status():
    return jsonify(states)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)