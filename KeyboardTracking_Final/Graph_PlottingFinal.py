import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

# Get user input from command line arguments
user_number = sys.argv[1]

# Directories
input_file = f"F:\\CODE\\pythonscripts\\FINAL\\KeyboardTracking_Final\\Raw Data\\raw_keystroke_data_{user_number}.txt"
save_dir = f"F:\\CODE\\pythonscripts\\FINAL\\KeyboardTracking_Final\\Graph_CSV\\participant_{user_number}"


# Ensure the save directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Function to generate a unique file name for CSV
def generate_unique_csv_filename(directory, base_name="keystroke_data_", extension="csv"):
    i = 1
    while True:
        filename = f"{base_name}{i}.{extension}"
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            return file_path
        i += 1

# Function to generate a unique file name for images
def generate_unique_image_filename(directory, base_name="keystroke_", extension="png"):
    i = 1
    while True:
        filename = f"{base_name}{i}.{extension}"
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            return file_path
        i += 1

# Read and parse the keystroke data
def read_keystroke_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            try:
                timestamp, event = line.split(", ")
                event_type, key_action = event.split(" ")
                data.append((float(timestamp.split(": ")[1]), event_type, key_action.strip()))
            except ValueError:
                continue  # Skip any lines that don't match the expected format
    return data

# Generate flight times
def process_keystroke_data(data):
    keystrokes = pd.DataFrame(data, columns=["Timestamp", "Type", "Action"])
    keystrokes['Timestamp'] = pd.to_datetime(keystrokes['Timestamp'], unit='s')
    keystrokes['Key'] = keystrokes['Action'].str.split().str[0]
    keystrokes['Action'] = keystrokes['Action'].str.split().str[1]

    # Calculate flight times
    keystrokes['Flight Time'] = keystrokes['Timestamp'].diff().dt.total_seconds().fillna(0)
    
    return keystrokes

# Generate and save plots
def plot_keystroke_data(df, save_dir):
    # Flight Times Histogram
    plt.figure(figsize=(10, 6))
    df['Flight Time'].hist(bins=30, alpha=0.7, range=(0, 1))
    plt.title('Keystroke Flight Times')
    plt.xlabel('Flight Time (s)')
    plt.ylabel('Frequency')
    plt.grid(False)
    flight_hist_path = generate_unique_image_filename(save_dir, base_name="keystroke_flight_times_")
    plt.savefig(flight_hist_path)
    plt.close()

    # Typing Speed Over Time
    df['Time Elapsed'] = (df['Timestamp'] - df['Timestamp'].iloc[0]).dt.total_seconds()
    df['CPM'] = (df.index / df['Time Elapsed']) * 60  # Characters per minute

    plt.figure(figsize=(10, 6))
    plt.plot(df['Time Elapsed'], df['CPM'])
    plt.title('Typing Speed Over Time')
    plt.xlabel('Time Elapsed (s)')
    plt.ylabel('Typing Speed (CPM)')
    plt.grid(True)
    speed_path = generate_unique_image_filename(save_dir, base_name="typing_speed_")
    plt.savefig(speed_path)
    plt.close()

# Main execution
keystroke_data = read_keystroke_data(input_file)
processed_data = process_keystroke_data(keystroke_data)
csv_path = generate_unique_csv_filename(save_dir, base_name="keystroke_data_")
processed_data.to_csv(csv_path, index=False)
plot_keystroke_data(processed_data, save_dir)

print(f"Graphs and CSV file have been saved in {save_dir}")
