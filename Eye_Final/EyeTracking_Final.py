import tobii_research as tr
import time
import threading
import os
import math
import numpy as np

save_dir = "F:\\CODE\\pythonscripts\\FINAL\\Eye_Final\\Raw Data"

# Ensure the save directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Function to generate a unique file name
def generate_unique_filename(directory, base_name="raw_eye_data_"):
    i = 1
    while True:
        filename = f"{base_name}{i}.txt"
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            return file_path
        i += 1

# Generate a unique file name
save_path = generate_unique_filename(save_dir)

# Screen dimensions
SCREEN_WIDTH = 1680
SCREEN_HEIGHT = 1050

# Function to convert normalized coordinates to pixel coordinates
def normalized_to_pixel_coords(normalized_coords, screen_width, screen_height):
    x, y = normalized_coords
    if np.isnan(x) or np.isnan(y):
        return None  # Return None if coordinates are NaN
    x = min(max(x, 0), 1) * screen_width
    y = min(max(y, 0), 1) * screen_height
    return int(x), int(y)

# Step 1: Find the Eye Tracker
found_eyetrackers = tr.find_all_eyetrackers()

tracking = False
tracking_thread = None

def gaze_data_callback(gaze_data):
    try:
        unix_timestamp = time.time()
        left_eye_normalized = gaze_data['left_gaze_point_on_display_area']
        right_eye_normalized = gaze_data['right_gaze_point_on_display_area']
        left_pupil = gaze_data['left_pupil_diameter']
        right_pupil = gaze_data['right_pupil_diameter']

        left_eye_pixel = normalized_to_pixel_coords(left_eye_normalized, SCREEN_WIDTH, SCREEN_HEIGHT)
        right_eye_pixel = normalized_to_pixel_coords(right_eye_normalized, SCREEN_WIDTH, SCREEN_HEIGHT)

        avg_eye_position = None
        if left_eye_pixel and right_eye_pixel:
            avg_eye_position = (int(np.floor((left_eye_pixel[0] + right_eye_pixel[0]) / 2)),
                                int(np.floor((left_eye_pixel[1] + right_eye_pixel[1]) / 2)))
        elif left_eye_pixel:
            avg_eye_position = left_eye_pixel
        elif right_eye_pixel:
            avg_eye_position = right_eye_pixel

        
        avg_pupil_dilation = None
        if not np.isnan(left_pupil) and not np.isnan(right_pupil):
            avg_pupil_dilation = (left_pupil + right_pupil) / 2
        elif not np.isnan(left_pupil):
            avg_pupil_dilation = left_pupil
        elif not np.isnan(right_pupil):
            avg_pupil_dilation = right_pupil

        data = (f"Unix Timestamp: {unix_timestamp}, "
                f"Left eye (normalized): {left_eye_normalized}, Right eye (normalized): {right_eye_normalized}, "
                f"Left eye (pixel): {left_eye_pixel}, Right eye (pixel): {right_eye_pixel}, "
                f"Average eye position (pixels): {avg_eye_position}, "
                f"Left pupil: {left_pupil}, Right pupil: {right_pupil}, "
                f"Average pupil dilation: {avg_pupil_dilation}")
        
        with open(save_path, 'a') as f:
            f.write(data + "\n")
    except Exception as e:
        print(f"Error while saving data: {e}")

def start_tracking(eyetracker):
    global tracking, save_path
    if not tracking:
        save_path = generate_unique_filename(save_dir)
        print(f"Saving data to {save_path}")
        print("Subscribing to gaze data...")
        eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
        tracking = True
        print("Started collecting gaze data.")
    else:
        print("Tracking is already running.")

def stop_tracking(eyetracker):
    global tracking
    if tracking:
        print("Unsubscribing from gaze data...")
        eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
        tracking = False
        print("Stopped collecting gaze data.")
    else:
        print("Tracking is not running.")

if found_eyetrackers:
    my_eyetracker = found_eyetrackers[0]
    print("Address: " + my_eyetracker.address)
    print("Model: " + my_eyetracker.model)
    print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
    print("Serial number: " + my_eyetracker.serial_number)

    while True:
        command = input("Type 's' to begin tracking or 'e' to end tracking: ").strip().lower()

        if command == 's':
            if tracking_thread is None or not tracking_thread.is_alive():
                tracking_thread = threading.Thread(target=start_tracking, args=(my_eyetracker,))
                tracking_thread.start()
            else:
                print("Tracking is already running.")
        elif command == 'e':
            stop_tracking(my_eyetracker)
            if tracking_thread is not None:
                tracking_thread.join()
        elif command == 'exit':
            if tracking:
                stop_tracking(my_eyetracker)
                if tracking_thread is not None:
                    tracking_thread.join()
            print("Exiting.")
            break
else:
    print("No eye trackers found.")
