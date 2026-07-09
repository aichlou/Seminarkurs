from flask import Flask, request, jsonify
import json
import manager

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
        items = manager.alleItems()
        items_json = json.dumps(items, indent=2)
        return items_json
    
@app.route('/isset')
def isset():
    return 'YES' 

@app.route('/send')
def send():
    name = request.args.get('name')
    beschreibung = request.args.get('beschreibung')
    return 'YES'

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
