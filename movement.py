import math
import threading
import time
from ev3dev2.motor import MoveJoystick, MoveTank, MediumMotor, SpeedPercent, OUTPUT_A, OUTPUT_B, OUTPUT_C

from utils import debug_print
import sockets

instruction_mapping = {
    "f": (-100, -100),  # forward
    "b": (100, 100),    # backward
    "r": (-100, 100),   # right
    "l": (100, -100),   # left
    "p": True,          # pickup
    "d": False,         # drop
    "t": (-100, 100)    # turn
}

def cms_to_deg(cms):
    return round(cms/0.02618)

def compute_deg_for_distance(distance: float, unit: str):
    if unit == "m":
        distance = distance * 100

    return cms_to_deg(distance)

_left_motor = OUTPUT_B
_right_motor = OUTPUT_A
_claw = OUTPUT_C

_joystick_move = MoveJoystick(_left_motor, _right_motor)
_instruction_move = MoveTank(_left_motor, _right_motor)
_claw = MediumMotor(_claw)

def claw(b):
        if b:
            _claw.on(SpeedPercent(25))
        else:
            _claw.off(False)
            _claw.on_for_degrees(SpeedPercent(25), -90)

def stop():
    _joystick_move.off()

timer = None

def joystick(x, y, radius=1):
    x = -x

    global timer
    if timer is not None:
        now = time.time()
        temp = now - timer
        timer = now

        debug_print(temp)
    else:
        timer = time.time()

    _joystick_move.on(x, y, radius)
    l_speed, r_speed = odometer.get_speed_joystick(x, y, radius)
    odometer.update_position(l_speed, r_speed)

def interpret(instruction: str):
    params = instruction.split("-")

    order = params[0]

    if len(params) == 1:
        if(order == 'p' or order == 'd'):
            claw(instruction_mapping[order])
            return
        elif order == 'l' or order == 'r':
            value = 0.75
            unit = 's'
    else:
        value = float(params[1])
        unit = params[2]

    speeds = instruction_mapping[order]

    if unit != "s":
        degrees = compute_deg_for_distance(value, unit) if unit != "d" else value
        _instruction_move.on_for_degrees(speeds[0], speeds[1], degrees)
    else:
        debug_print("speeds ", speeds)
        _instruction_move.on_for_seconds(speeds[0], speeds[1], value)

#TODO: Send position when operating under voice instructions too
# This mostly seems to work, but it's not perfect. Can't verify positional and angle data until the map is debugged in the app
def send_position():
    try:
        while True:
            data = str(odometer.x) + ";" + str(odometer.y) + ";" + str(odometer.theta) + sockets.message_end
            #debug_print("\nSent: " + data + "\n")
            sockets.emitters.position.send(data.encode())
    except ConnectionError:
        sockets.clear()

def start_tracking():
    sensor_thread = threading.Thread(target=send_position)
    sensor_thread.daemon = True
    sensor_thread.start()

class Odometer:
    wheel_distance = 15.5 # cm
    # This value came from averaging the time between (19) calls of the joystick function
    # I do not know why it takes 0.6 seconds on average to call it, but such is life
    delta_t = 0.60753235064055 # seconds
    # This is the approximate distance traveled when both motors operate at 100% speed for 1 second
    distance = 24.2
    unit = 30 # cm

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

    def get_speed_joystick(self, x, y, radius):
        vector_length = math.sqrt((x * x) + (y * y))
        angle = math.degrees(math.atan2(y, x))

        if angle < 0:
            angle += 360

        if vector_length > radius:
            vector_length = radius

        (init_left_speed_percentage, init_right_speed_percentage) = MoveJoystick.angle_to_speed_percentage(angle)

        left_speed_percentage = (init_left_speed_percentage * vector_length) / radius
        right_speed_percentage = (init_right_speed_percentage * vector_length) / radius

        return self.speed_to_cms(left_speed_percentage), self.speed_to_cms(right_speed_percentage)

    def update_position(self, v_left, v_right):
        v = (v_left + v_right) / 2
        omega = (v_right - v_left) / self.wheel_distance
        delta_theta = omega * self.delta_t

        delta_x = v * math.cos(self.theta + delta_theta / 2) * self.delta_t
        delta_y = v * math.sin(self.theta + delta_theta / 2) * self.delta_t

        debug_print("\nOmega: " + str(omega))
        debug_print("delta_x: " + str(delta_x) + " delta_y: " + str(delta_y) + " delta_theta: " + str(delta_theta) + "\n")

        # delta_x and delta_y are in cm
        # Divide by unit to normalize it, so every unit is equal to 30 cm
        self.x += delta_x / self.unit
        self.y += delta_y / self.unit
        self.theta += delta_theta

        return self.x, self.y, self.theta

    def speed_to_cms(self, speed):
        return speed / 100 * self.distance

odometer = Odometer()
