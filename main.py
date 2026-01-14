import time
import threading
import webserver
import motor

thread = threading.Thread(target=motor.rotate())