import subprocess
import time

# Paths to your scripts
mouse_tracking_script = "F:\\CODE\\pythonscripts\\FINAL\\Mouse_Final\\MouseTracking_Final.py"
eye_tracking_script = "F:\\CODE\\pythonscripts\\FINAL\\Eye_Final\\EyeTracking_Final.py"
keyboard_tracking_script = "F:\\CODE\\pythonscripts\\FINAL\\KeyboardTracking_Final\\Keyboard_Final.py"
arduino_script = "F:\\CODE\\pythonscripts\\FINAL\\MASTER_SCRIPT\\ArduinoEmailStartEnd.py"

# Start each script
mouse_process = subprocess.Popen(["python", mouse_tracking_script], stdin=subprocess.PIPE)
eye_process = subprocess.Popen(["python", eye_tracking_script], stdin=subprocess.PIPE)
keyboard_process = subprocess.Popen(["python", keyboard_tracking_script], stdin=subprocess.PIPE)
arduino_process = subprocess.Popen(["python", arduino_script])

def send_input(process, input_str):
    process.stdin.write(input_str.encode())
    process.stdin.flush()

# Function to start all processes
def start_tracking():
    send_input(mouse_process, 's\n')
    send_input(eye_process, 's\n')
    send_input(keyboard_process, 's\n')
    print("Tracking started for all scripts.")

# Function to stop all processes
def stop_tracking():
    send_input(mouse_process, 'e\n')
    send_input(eye_process, 'e\n')
    send_input(keyboard_process, 'e\n')
    print("Stop signal sent to all scripts.")

try:
    while True:
        command = input("Enter 'start' to begin tracking, 'stop' to end tracking, or 'exit' to quit: ").strip().lower()
        if command == 'start':
            start_tracking()
        elif command == 'stop':
            stop_tracking()
        elif command == 'exit':
            stop_tracking()
            break
        else:
            print("Invalid command. Please enter 'start', 'stop', or 'exit'.")
except KeyboardInterrupt:
    print("\nExiting...")
    stop_tracking()

# Wait for all processes to complete (this will block until all scripts finish)
mouse_process.wait()
eye_process.wait()
keyboard_process.wait()
arduino_process.wait()

print("All tracking scripts have completed and saved their files.")
