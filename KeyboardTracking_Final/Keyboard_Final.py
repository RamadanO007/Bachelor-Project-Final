import os
import time
import threading
from pynput import keyboard

class KeystrokeDynamics:
    def __init__(self):
        self.key_press_times = {}
        self.key_release_times = {}
        self.key_sequences = []
        self.start_time = None
        self.total_chars = 0
        self.recording = False
        self.save_dir = "F:\\CODE\\pythonscripts\\FINAL\\KeyboardTracking_Final\\Raw Data"
        self.ensure_save_directory()
        self.file_path = self.generate_unique_filename()

    def ensure_save_directory(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def generate_unique_filename(self, base_name="raw_keystroke_data_"):
        i = 1
        while True:
            filename = f"{base_name}{i}.txt"
            file_path = os.path.join(self.save_dir, filename)
            if not os.path.exists(file_path):
                return file_path
            i += 1

    def on_press(self, key):
        if not self.recording:
            return

        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)

        press_time = time.time()
        self.key_press_times[key_char] = press_time
        self.key_sequences.append((key_char, 'press', press_time))

    def on_release(self, key):
        if not self.recording:
            return

        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)

        release_time = time.time()
        self.key_release_times[key_char] = release_time
        self.key_sequences.append((key_char, 'release', release_time))
        self.total_chars += 1

    def start_listening(self):
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()

    def calculate_dwell_times(self):
        dwell_times = {}
        for key, press_time in self.key_press_times.items():
            if key in self.key_release_times:
                dwell_times[key] = self.key_release_times[key] - press_time
        return dwell_times

    def calculate_flight_times(self):
        flight_times = []
        for i in range(1, len(self.key_sequences)):
            if self.key_sequences[i-1][1] == 'release' and self.key_sequences[i][1] == 'press':
                flight_time = self.key_sequences[i][2] - self.key_sequences[i-1][2]
                flight_times.append((self.key_sequences[i-1][0], self.key_sequences[i][0], flight_time))
        return flight_times

    def calculate_typing_speed(self):
        if not self.start_time:
            return 0
        total_time = time.time() - self.start_time
        return self.total_chars / total_time * 60  # characters per minute

    def save_data(self):
        with open(self.file_path, 'w') as file:
            for key, action, timestamp in self.key_sequences:
                file.write(f"Unix Timestamp: {timestamp}, {key} {action}\n")
            dwell_times = self.calculate_dwell_times()
            flight_times = self.calculate_flight_times()
            typing_speed = self.calculate_typing_speed()

            file.write("\nDwell Times:\n")
            for key, time in dwell_times.items():
                file.write(f"{key}: {time}\n")

            file.write("\nFlight Times:\n")
            for (key1, key2, time) in flight_times:
                file.write(f"{key1} to {key2}: {time}\n")

            file.write(f"\nTyping Speed: {typing_speed} CPM\n")

    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        print("Recording started...")

    def stop_recording(self):
        self.recording = False
        self.save_data()
        print("Recording stopped and data saved.")

kd = KeystrokeDynamics()

def listen_to_keyboard():
    kd.start_listening()

def monitor_terminal():
    while True:
        command = input("Type 's' to begin recording or 'e' to end recording: ").strip().lower()
        if command == "s":
            kd.start_recording()
        elif command == "e":
            kd.stop_recording()
            break

# Start the keyboard listener in a separate thread
keyboard_thread = threading.Thread(target=listen_to_keyboard)
keyboard_thread.start()

# Monitor the terminal for start/stop commands
monitor_terminal()
