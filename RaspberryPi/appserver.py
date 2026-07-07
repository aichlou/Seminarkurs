from flask import Flask, request, jsonify

app = Flask(__name__)
isInit: Optional[bool] = None
counter = 0

@app.route('/message')
def recieve_message():
    return "Alles Gude"

@app.route('/fetch')
def fetch():
    if counter < 20:
        return 'init'
    else:
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
            "10": {"name": "Bob", "age": 35},
            "11": {"name": "Max", "age": 30},
            "12": {"name": "Anna", "age": 25},
            "13": {"name": "Bob", "age": 35},
        })
    
@app.route('/init')
def init():
    global counter, isInit
    counter = counter + 1
    if counter > 20:
        isInit = False
    if isInit is None:
        isInit = True
        return 'OK'
    elif isInit is True:
        return 'IS'
    elif isInit is False:
        return 'NO'
    else:
        return 'Error'
    
@app.route('/return')
def ret():
    id = request.args.get('id')
    return "id"
    
@app.errorhandler(404)
def not_found(error):
    return "Error: Route nicht gefunden"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
