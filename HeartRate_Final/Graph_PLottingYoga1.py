import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import sys

# Get user input from terminal
user_number = input("Enter user number: ")

# Directories
input_file = f"F:\\CODE\\pythonscripts\\FINAL\\HeartRate_Final\\Raw Data\\hr_data_hrv_{user_number}.txt"
timestamps_file = f"F:\\CODE\\pythonscripts\\FINAL\\MASTER_SCRIPT\\Assets\\timestamps_{user_number}.txt"
save_dir = f"F:\\CODE\\pythonscripts\\FINAL\\HeartRate_Final\\Graphs_CSV\\participant_{user_number}"

# Ensure the save directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Function to generate a unique file name
def generate_unique_filename(directory, base_name="heart_rate_data_", extension="csv"):
    i = 1
    while True:
        filename = f"{base_name}{i}.{extension}"
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            return file_path
        i += 1

# Function to generate a unique file name for images
def generate_unique_image_filename(directory, base_name="heart_rate_over_time_", extension="png"):
    i = 1
    while True:
        filename = f"{base_name}{i}.{extension}"
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            return file_path
        i += 1

# Read the raw data (assumed CSV format with two columns)
data = pd.read_csv(input_file)

# Rename columns to be consistent
data.columns = ['HR', 'SDNN']

# Add a timestamp column to simulate real-time data (assumes 1-second intervals)
data['Timestamp'] = pd.date_range(start='1/1/2020', periods=len(data), freq='S')

# Save raw data to a new CSV file
csv_save_path = generate_unique_filename(save_dir, base_name="heart_rate_data_", extension="csv")
data.to_csv(csv_save_path, index=False)

# Read timestamps
with open(timestamps_file, 'r') as f:
    timestamps = f.read()

# Parse timestamps
start_times = list(map(float, re.findall(r'\d+', re.search(r'email_start_times = \[(.*?)\]', timestamps, re.DOTALL).group(1))))
end_times = list(map(float, re.findall(r'\d+', re.search(r'email_end_times = \[(.*?)\]', timestamps, re.DOTALL).group(1))))

# Convert timestamp to datetime for better plotting
data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='s')
start_times = [pd.to_datetime(ts, unit='s') for ts in start_times]
end_times = [pd.to_datetime(ts, unit='s') for ts in end_times]

# Define global min and max values for SDNN for uniform y-axis
global_min_sdnn = 0
global_max_sdnn = 50

# Plot heart rate, and SDNN for each email reading period
for i in range(12):
    start_time = start_times[i]
    end_time = end_times[i]
    email_data = data[(data['Timestamp'] >= start_time) & (data['Timestamp'] < end_time)]
    
    # Calculate elapsed time in seconds
    email_data['Elapsed_Time'] = (email_data['Timestamp'] - start_time).dt.total_seconds()
    email_data['Elapsed_Time'] = email_data['Elapsed_Time'] - email_data['Elapsed_Time'].min()  # Ensure x-axis starts at 0
    
    # Heart Rate graph
    plt.figure()
    plt.plot(email_data['Elapsed_Time'], email_data['HR'], label=f'Email {i+1} Heart Rate')
    plt.xlabel('Elapsed Time (s)')
    plt.ylabel('Heart Rate')
    plt.ylim(50, 120)  # Set y-axis from 50 to 120 for HR
    plt.xlim(0, (email_data['Elapsed_Time'].max() // 10 + 1) * 10)  # Ensure uniform intervals of 10s
    plt.xticks(range(0, int(email_data['Elapsed_Time'].max()) + 1, 10))  # Set x-axis ticks every 10 seconds
    plt.title(f'Heart Rate during Email {i+1}')
    plt.legend()
    plt.tight_layout()
    image_save_path = generate_unique_image_filename(save_dir, base_name=f"heart_rate_email_{i+1}_", extension="png")
    plt.savefig(image_save_path)
    plt.close()

    # SDNN graph
    plt.figure()
    plt.plot(email_data['Elapsed_Time'], email_data['SDNN'], label='SDNN', color='orange')
    plt.xlabel('Elapsed Time (s)')
    plt.ylabel('SDNN')
    plt.xlim(0, (email_data['Elapsed_Time'].max() // 10 + 1) * 10)  # Ensure uniform intervals of 10s
    plt.xticks(range(0, int(email_data['Elapsed_Time'].max()) + 1, 10))  # Set x-axis ticks every 10 seconds
    plt.ylim(global_min_sdnn, global_max_sdnn)  # Set y-axis based on the global min/max SDNN
    plt.title(f'SDNN during Email {i+1}')
    plt.legend()
    plt.tight_layout()
    image_save_path = generate_unique_image_filename(save_dir, base_name=f"sdnn_email_{i+1}_", extension="png")
    plt.savefig(image_save_path)
    plt.close()

# Plot HR and SDNN over total time
data['Elapsed_Time_Total'] = (data['Timestamp'] - data['Timestamp'].iloc[0]).dt.total_seconds()
data['Elapsed_Time_Total'] = data['Elapsed_Time_Total'] - data['Elapsed_Time_Total'].min()  # Ensure x-axis starts at 0

# HR over total time
plt.figure()
plt.plot(data['Elapsed_Time_Total'], data['HR'], label='Heart Rate')
plt.xlabel('Elapsed Time (s)')
plt.ylabel('Heart Rate')
plt.ylim(50, 120)  # Ensure y-axis is always 50 to 120 for HR
plt.xticks(range(0, int(data['Elapsed_Time_Total'].max()) + 1, 10))  # Set x-axis ticks every 10 seconds
plt.title('Heart Rate over Total Time')
plt.legend()
plt.tight_layout()
hr_total_time_path = generate_unique_image_filename(save_dir, base_name="heart_rate_total_time_", extension="png")
plt.savefig(hr_total_time_path)
plt.close()

# SDNN over total time
plt.figure()
plt.plot(data['Elapsed_Time_Total'], data['SDNN'], label='SDNN', color='orange')
plt.xlabel('Elapsed Time (s)')
plt.ylabel('SDNN')
plt.xticks(range(0, int(data['Elapsed_Time_Total'].max()) + 1, 10))  # Set x-axis ticks every 10 seconds
plt.ylim(global_min_sdnn, global_max_sdnn)  # Ensure y-axis matches SDNN graphs
plt.title('SDNN over Total Time')
plt.legend()
plt.tight_layout()
sdnn_total_time_path = generate_unique_image_filename(save_dir, base_name="sdnn_total_time_", extension="png")
plt.savefig(sdnn_total_time_path)
plt.close()

print(f"Raw data saved to: {csv_save_path}")
print(f"Graphs saved in directory: {save_dir}")
