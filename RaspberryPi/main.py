import time
import threading
import webserver
import motor
import sensor
from queue import Queue, Empty
import init


def temp(index, value):
    webserver.set_state(index, value)
    print(f"State {index} auf {value} gesetzt")
    time.sleep(5)
    webserver.set_state(index, not value)
    print(f"State {index} auf {not value} gesetzt")


def main():
    commands = Queue()
    sensordata = Queue()

    host_thread = threading.Thread(
        target=webserver.host_server,
        args=(commands,),
        daemon=True,
    )
    host_thread.start()
    print("Hosting Webserver")

    motor.setup_motors()
    print("Motors are set up")

    sensor_thread = threading.Thread(
        target=sensor.read_sensors,
        args=(commands,),
        daemon=True,
    )
    sensor_thread.start()

    try:
        while True:
            print("Warte auf Befehle...")
            try:
                cmd = commands.get(timeout=1)
            except Empty:
                continue

            command, *args = cmd
            match command:
                case "start_motor":
                    print("Starting motor thread")
                    rotate_thread = threading.Thread(target=motor.rotate, args=args, daemon=True)
                    rotate_thread.start()
                case "change_state":
                    state_thread = threading.Thread(target=webserver.set_state, args=args, daemon=True)
                    state_thread.start()
                    sensordata.put(tuple(args))
                case "stop_motor":
                    print("Stopping motor")
                    motor.stop_motor(args[0])
                case "init":
                    print("Initializing system")
                    init_thread = threading.Thread(target=init.init, args=(sensordata, commands), daemon=True)
                    init_thread.start()
                case _:
                    print(f"Unbekannter Befehl erhalten: {command}")
    except KeyboardInterrupt:
        print("Programm wird beendet...")
    except Exception as exc:
        print("Fehler in der Hauptschleife:", exc)
    finally:
        motor.cleanup()


if __name__ == "__main__":
    main()
