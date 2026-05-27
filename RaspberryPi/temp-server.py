from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/message')
def recieve_message():
    return "Alles Gude"

@app.route('/fetch')
def fetch():
    return jsonify({
        "1": {"name": "Max", "age": 20},
        "2": {"name": "Anna", "age": 25},
        "3": {"name": "Bob", "age": 35},
        "4": {"name": "Lennards", "age": 30},
        "5": {"name": "Anna", "age": 25},
        "6": {"name": "Bob", "age": 35},
        "7": {"name": "Max", "age": 30},
        "8": {"name": "Anna", "age": 25},
        "9": {"name": "Bob", "age": 35},
    })

@app.errorhandler(404)
def not_found(error):    
    return "Error: Route nicht gefunden"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)