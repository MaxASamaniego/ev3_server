#!/usr/bin/env python3

import sockets
import sensors
import speech
import movement

from utils import *

def main():
    reset_console()
    set_cursor(False)
    set_font('Lat15-Terminus24x12')

    sockets.initialize()

    reset_console()
    print("Iniciando...")
    speak_es("Conectado")

    sensors.start()
    speech.start()
    movement.start_tracking()

    reset_console()
    print("")

    while True:
        data = sockets.receivers.client.recv(1024)

        if not data:
            break

        data = data.decode()

        data = data.split(sockets.message_end)[-2]
        data = data.split(":")

        mode = data[0]
        data = "".join(data[1:])

        debug_print("mode:" + mode + " data:" + data)

        if mode == "text":
            data = data.split(";")

            for instruction in data:
                movement.interpret(instruction)

            continue


        if "*" in data:
            movement.stop()
            is_clawing_time = data[data.index("*") + 2] == "1"
        else:
            joy_x = float(data[0:5])
            joy_y = float(data[6:11])
            is_clawing_time = data[12] == "1"
            movement.joystick(joy_x, joy_y)

        movement.claw(is_clawing_time)


if __name__ == '__main__':
    try:
        main()
    finally:
        sockets.clear()
