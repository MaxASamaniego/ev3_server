import threading

from ev3dev2.sensor import INPUT_4
from ev3dev2.sensor.lego import InfraredSensor

import sockets

ir_sensor = InfraredSensor(INPUT_4)

def send_sensor_data():
        try:
            while True:
                data = "ir:" + str(ir_sensor.proximity) + sockets.message_end
                sockets.emitters.sensor.send(data.encode())
        except ConnectionError:
            sockets.clear()

def start():
    sensor_thread = threading.Thread(target=send_sensor_data)
    sensor_thread.daemon = True
    sensor_thread.start()
