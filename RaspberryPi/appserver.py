from flask import Flask, request, jsonify
import json
import manager
import state


def host_server(commands):
    app = Flask(__name__)

    @app.route('/message')
    def recieve_message():
        return "Alles Gude"

    @app.route('/fetch')
    def fetch():
        if not state.was_init:
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
        if not state.was_init:
            commands.put(("init",))
            state.was_init = True
            return 'OK'
        elif state.init_complete:
            return 'NO'
        else:
            return 'IS'
        
    @app.route('/return')
    def ret():
        id = request.args.get('id')
        return "id"
        
    @app.errorhandler(404)
    def not_found(error):
        return "Error: Route nicht gefunden"

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5001)
