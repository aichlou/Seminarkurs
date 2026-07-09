from flask import Flask, request, jsonify
import json
import manager
import state
from typing import Optional

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
        fach_id = manager.emptySpace()
        manager.bearbeite_fach(fach_id, name, beschreibung)
        commands.put(("send", fach_id))
        return 'YES'
    
    @app.route('/return')
    def ret():
        id = request.args.get('id')
        items = manager.alleItems()
        fach_id = items.get(id)
        manager.bearbeite_fach(fach_id, None, None, None)
        return "id"
        
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
        
    @app.errorhandler(404)
    def not_found(error):
        return "Error: Route nicht gefunden"

    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
