import socket
from utils import debug_print, beep

class _Receivers:
    def __init__(self, receiver_map: dict):
        self.client = None
        self.speech = None
        for key, value in receiver_map.items():
            setattr(self, key, value)


class _Emitters:
    def __init__(self, emitter_map: dict):
        self.sensor = None
        self.position = None
        for key, value in emitter_map.items():
            setattr(self, key, value)

receivers = None
emitters = None

message_end = "|"

_sockets = []

_initialized = False

def initialize():
    global _initialized

    if _initialized:
        return

    host = socket.gethostbyname(socket.gethostname())
    debug_print("EV3 brick IP: " + host)
    port = 8000
    sensor_port = 8001
    speech_port = 8002
    position_port = 8003

    print(host)

    main_socket = socket.socket()
    main_socket.bind((host, port))
    _sockets.append(main_socket)

    sensor_socket = socket.socket()
    sensor_socket.bind((host, sensor_port))
    _sockets.append(sensor_socket)

    speech_socket = socket.socket()
    speech_socket.bind((host, speech_port))
    _sockets.append(speech_socket)

    position_socket = socket.socket()
    position_socket.bind((host, position_port))
    _sockets.append(position_socket)

    main_socket.listen(1)
    sensor_socket.listen(1)
    speech_socket.listen(1)
    position_socket.listen(1)
    debug_print("Server listening")
    beep()

    client, addr = main_socket.accept()
    sensor_emitter, s_addr1 = sensor_socket.accept()
    speech_receiver, s_addr2 = speech_socket.accept()
    position_emitter, s_addr3 = position_socket.accept()

    _sockets.append(client)
    _sockets.append(sensor_emitter)
    _sockets.append(speech_receiver)
    _sockets.append(position_emitter)

    debug_print("Connection accepted from: " + str(addr[0]) + ':' + str(addr[1]))

    receiver_map = {"client": client, "speech": speech_receiver}
    emitter_map = {"sensor": sensor_emitter, "position": position_emitter}

    global receivers, emitters
    receivers = _Receivers(receiver_map)
    emitters = _Emitters(emitter_map)

    _initialized = True

def clear():
    for sock in _sockets:
        sock.close()
