import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import sys

# Get user input from command line arguments
# change to a user input from the terminal

user_number = input("Please enter the user number: ")
# user_number = sys.argv[1]


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

# Read the raw data
data = pd.read_csv(input_file, sep='\t')

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

# Debugging Output: Print parsed timestamps
print(f"Parsed start times: {start_times}")
print(f"Parsed end times: {end_times}")

# Ensure correct parsing by printing the start and end time differences
for i in range(len(start_times)):
    print(f"Email {i+1}: Start Time = {start_times[i]}, End Time = {end_times[i]}, Duration = {end_times[i] - start_times[i]} seconds")

# Plot heart rate, RMSSD, and SDNN for each email reading period
for i in range(12):
    start_time = pd.to_datetime(start_times[i], unit='s')
    end_time = pd.to_datetime(end_times[i], unit='s')
    email_data = data[(data['Timestamp'] >= start_time) & (data['Timestamp'] <= end_time)]
    
    # Calculate elapsed time in seconds
    email_data['Elapsed_Time'] = (email_data['Timestamp'] - start_time).dt.total_seconds()
    
    # Debugging Output: Check the range of elapsed times
    print(f"Email {i+1}: Elapsed time starts at {email_data['Elapsed_Time'].min()} and ends at {email_data['Elapsed_Time'].max()}")

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
