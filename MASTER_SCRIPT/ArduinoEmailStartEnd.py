import serial
import time
import os

# Set up the serial port
ser = serial.Serial('COM4', 9600)  

# Define the save directory
save_dir = r"F:\CODE\pythonscripts\FINAL\MASTER_SCRIPT\Assets"

# Ensure the save directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Function to generate a unique file name for the log file
def generate_unique_filename(directory, base_name="timestamps_", extension="txt"):
    i = 1
    while True:
        filename = f"{base_name}{i}.{extension}"
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            return file_path
        i += 1

# Generate a unique file name
file_path = generate_unique_filename(save_dir)

# Initialize counters and arrays for start and end events
start_count = 0
end_count = 0
email_start_times = []
email_end_times = []

# Function to save arrays to a file
def save_arrays_to_file(start_times, end_times, file_path):
    with open(file_path, 'w') as file:
        file.write("email_start_times = [\n")
        for time in start_times:
            file.write(f"    {time},\n")
        file.write("]\n\n")
        file.write("email_end_times = [\n")
        for time in end_times:
            file.write(f"    {time},\n")
        file.write("]\n")

# Open the serial port and start reading data
while True:
    if ser.in_waiting:
        try:
            # Read the serial data
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            
            # Split the data into time and event
            millis, event = data.split(' ', 1)
            
            # Convert the millis to UNIX timestamp
            arduino_start_time = time.time() - (int(millis) / 1000)
            unix_timestamp = arduino_start_time + (int(millis) / 1000)
            int_timestamp = int(unix_timestamp)

            # Log the UNIX timestamp to the appropriate array if not the first event
            if event == "email start":
                start_count += 1
                if start_count > 1 and len(email_start_times) < 12:
                    email_start_times.append(int_timestamp)
                    print(f"{int_timestamp} email start {start_count}")
            elif event == "email end":
                end_count += 1
                if end_count > 1 and len(email_end_times) < 12:
                    email_end_times.append(int_timestamp)
                    print(f"{int_timestamp} email end {end_count}")

            # Save arrays to file when both are full
            if len(email_start_times) == 12 and len(email_end_times) == 12:
                save_arrays_to_file(email_start_times, email_end_times, file_path)
                print("Saved arrays to file.")
                break

        except Exception as e:
            print(f"Error processing data: {e}")

    time.sleep(0.1)
