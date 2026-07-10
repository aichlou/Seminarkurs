import time
import threading
import webserver
import motor
import sensor
import appserver
from queue import Queue, Empty
import init

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
    
    app_thread = threading.Thread(
        target=appserver.host_server,
        args=(commands,),
        daemon=True
    )
    app_thread.start()
    print("Hosting Appserver")

    motor.setup_motors()
    print("Motors are set up")

    sensor_thread = threading.Thread(
        target=sensor.read_sensors,
        args=(commands,),
        daemon=True,
    )
    sensor_thread.start()
    #motor_thread = threading.Thread(target=motor.temp, args=(), daemon=True)
    #motor_thread.start()
    print("Motor temp thread started")
    try:
        while True:
            try:
                cmd = commands.get(timeout=1)
            except Empty:
                continue

            command, *args = cmd
            match command:
                case "send":
                    print("Going to Position")
                    send_thread = threading.Thread(target=motor.send, args=args, daemon=True)
                    send_thread.start()
                case "return":
                    print("Going to Position")
                    ret_thread = threading.Thread(target=motor.ret, args=args, daemon=True)
                    ret_thread.start()
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
                case "0":
                    motor.set_null()
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
