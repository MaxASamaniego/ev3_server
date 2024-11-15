# ev3_server
These scripts serve the purpose of interpreting instructions received from the ev3_client mobile app and executing them on the ev3 robot.

Each module serves a different purpose.

- `main.py`: This is the main module. It is responsible for initializing the server and starting the threads for the other modules.
- `sockets.py`: This module handles the communication between the server (robot) and the client (mobile app) via TCP sockets.
- `sensors.py`: This module handles the sensor information on the ev3 robot.
- `speech.py`: This module handles the speech function of the robot.
- `movement.py`: This module handles the communication between the client and the motors on the ev3 robot.

