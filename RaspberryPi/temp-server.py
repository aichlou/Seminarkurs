from flask import Flask, request

app = Flask(__name__)

@app.route('/message')
def recieve_message():
    return "Alles Gude"

@app.route('/fetch')
def fetch():
    return "Kein Inhalt"

@app.errorhandler(404)
def not_found(error):    
    return "Error: Route nicht gefunden"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)