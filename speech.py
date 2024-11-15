import threading
import sockets
from utils import speak_es

def speak():
    try:
        while True:
            data = sockets.receivers.speech.recv(1024)
            if not data:
                continue
            data = data.decode()
            speak_es(data)
    except:
        sockets.clear()

def start():
    speech_thread = threading.Thread(target=speak)
    speech_thread.daemon = True
    speech_thread.start()
