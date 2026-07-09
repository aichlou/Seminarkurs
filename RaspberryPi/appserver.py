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
        print("Fahre um Elemnt in Fach {fach_id} zu lagern")
        return 'YES'
    
    @app.route('/return')
    def ret():
        fach_id = request.args.get('id')
        if not fach_id:
            return 'Error: id parameter missing', 400
        
        items = manager.alleItems()
        if fach_id not in items:
            return 'Error: Item not found', 404
        
        manager.bearbeite_fach(fach_id, None, None, None)
        commands.put(("return", fach_id))
        print("Fahre um Elemnt von Fach {fach_id} aus dem Lager zu holen")
        return 'OK'
        
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
