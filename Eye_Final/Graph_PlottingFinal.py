import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image
import re
import sys

# Get user input from command line arguments
user_number = sys.argv[1]
sequence = sys.argv[2]

# The rest of your code remains the same...

# Directories
input_file = f"F:\\CODE\\pythonscripts\\FINAL\\Eye_Final\\Raw Data\\raw_eye_data_{user_number}.txt"
timestamps_file = f"F:\\CODE\\pythonscripts\\FINAL\\MASTER_SCRIPT\\Assets\\timestamps_{user_number}.txt"
save_dir = f"F:\\CODE\\pythonscripts\\FINAL\\Eye_Final\\Graph_CSV\\participant_{user_number}"

# Ensure the save directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Email sequences dictionary
email_sequences = {
    "A": ["Online_Study.png", "Lecture_Invitation.png", "Library_Invitation.png", "Freedom_Words_Invitation.png", 
          "Online_Dating_study.png", "Children_Study_Invitation.png", "Teaching_Course.png", "VR_Study.png", 
          "Chat_GPT_talk.png", "NMUN_Info.png", "Philosophy_Workshop.png", "Fitness_Exercise.png"],
    "B": ["Online_Study.png", "Philosophy_Workshop.png", "Fitness_Exercise.png", "VR_Study.png", 
          "NMUN_Info.png", "Chat_GPT_talk.png", "Teaching_Course.png", "Online_Dating_study.png", 
          "Children_Study_Invitation.png", "Lecture_Invitation.png", "Library_Invitation.png", "Freedom_Words_Invitation.png"],
    "C": ["Library_Invitation.png", "Online_Study.png", "Lecture_Invitation.png", "Freedom_Words_Invitation.png", 
          "Children_Study_Invitation.png", "Online_Dating_study.png", "Chat_GPT_talk.png", "Teaching_Course.png", 
          "VR_Study.png", "NMUN_Info.png", "Fitness_Exercise.png", "Philosophy_Workshop.png"],
    "D": ["Online_Study.png", "Library_Invitation.png", "Freedom_Words_Invitation.png", "Online_Dating_study.png", 
          "Lecture_Invitation.png", "Children_Study_Invitation.png", "Teaching_Course.png", "Chat_GPT_talk.png", 
          "Philosophy_Workshop.png", "NMUN_Info.png", "Fitness_Exercise.png", "VR_Study.png"],
    "E": ["Library_Invitation.png", "Freedom_Words_Invitation.png", "Online_Study.png", "Lecture_Invitation.png", 
          "Online_Dating_study.png", "Children_Study_Invitation.png", "Chat_GPT_talk.png", "NMUN_Info.png", 
          "Teaching_Course.png", "VR_Study.png", "Philosophy_Workshop.png", "Fitness_Exercise.png"],
    "F": ["Library_Invitation.png", "Online_Study.png", "Freedom_Words_Invitation.png", "Lecture_Invitation.png", 
          "Children_Study_Invitation.png", "Online_Dating_study.png", "Chat_GPT_talk.png", "Teaching_Course.png", 
          "NMUN_Info.png", "VR_Study.png", "Fitness_Exercise.png", "Philosophy_Workshop.png"]
}

# Get the correct sequence of email images
email_images = email_sequences[sequence]

# Read timestamps
with open(timestamps_file, 'r') as f:
    timestamps = f.read()

# Debugging output
print(f"Timestamps file contents: {timestamps}")

# Parse timestamps
start_times = list(map(float, re.findall(r'\d+', re.search(r'email_start_times = \[(.*?)\]', timestamps, re.DOTALL).group(1))))
end_times = list(map(float, re.findall(r'\d+', re.search(r'email_end_times = \[(.*?)\]', timestamps, re.DOTALL).group(1))))

# Debugging output
print(f"Start times: {start_times}")
print(f"End times: {end_times}")

if len(start_times) != 12 or len(end_times) != 12:
    raise ValueError("The timestamps file does not contain the correct number of start and end times.")

# Function to generate a unique file name for images
def generate_unique_image_filename(directory, base_name="eye_graph_", extension="png"):
    i = 1
    while True:
        filename = f"{base_name}{i}.{extension}"
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            return file_path
        i += 1

# Function to add email image background
def plot_with_background(ax, image_path):
    img = Image.open(image_path)
    ax.imshow(img, extent=[0, img.width, img.height, 0], aspect='auto')
    return ax

# Regular expression patterns for parsing the data
timestamp_pattern = re.compile(r"Unix Timestamp: ([\d\.]+)")
eye_position_pattern = re.compile(r"Average eye position \(pixels\): \(([^,]+), ([^,]+)\)")
pupil_dilation_pattern = re.compile(r"Average pupil dilation: ([\d\.]+)")

# Read the raw eye data
data = []
with open(input_file, 'r') as file:
    for line in file:
        timestamp_match = timestamp_pattern.search(line)
        eye_position_match = eye_position_pattern.search(line)
        pupil_dilation_match = pupil_dilation_pattern.search(line)
        
        if timestamp_match and eye_position_match and pupil_dilation_match:
            timestamp = float(timestamp_match.group(1))
            avg_eye_pos_x = float(eye_position_match.group(1))
            avg_eye_pos_y = float(eye_position_match.group(2))
            avg_pupil_dilation = float(pupil_dilation_match.group(1))
            data.append({
                'Unix Timestamp': timestamp,
                'Average eye position (pixels)': (avg_eye_pos_x, avg_eye_pos_y),
                'Average pupil dilation': avg_pupil_dilation
            })

# Convert to DataFrame
df = pd.DataFrame(data)

# Filter out rows with all NaN values
df = df.dropna(how='all')

# Save the raw data to CSV
raw_data_file = generate_unique_image_filename(save_dir, base_name="raw_eye_data_", extension="csv")
df.to_csv(raw_data_file, index=False)

# Define AOIs based on specific parts of the email
aoi_definitions = {
    'Sender Email': {'x_range': (460, 710), 'y_range': (255, 300)},
    'Email Header': {'x_range': (460, 1630), 'y_range': (330, 440)},
    'Main Content': {'x_range': (448, 1680), 'y_range': (440, 739)},
    'Footer': {'x_range': (450, 1680), 'y_range': (740, 1000)},
    'Inbox and Folders': {'x_range': (145, 440), 'y_range': (170, 645)},
}

# Assign AOIs to eye events
df['aoi'] = 'Other'
for aoi, coords in aoi_definitions.items():
    x_range, y_range = coords['x_range'], coords['y_range']
    df.loc[(df['Average eye position (pixels)'].apply(lambda p: p[0] if isinstance(p, tuple) else np.nan) >= x_range[0]) &
           (df['Average eye position (pixels)'].apply(lambda p: p[0] if isinstance(p, tuple) else np.nan) < x_range[1]) &
           (df['Average eye position (pixels)'].apply(lambda p: p[1] if isinstance(p, tuple) else np.nan) >= y_range[0]) &
           (df['Average eye position (pixels)'].apply(lambda p: p[1] if isinstance(p, tuple) else np.nan) < y_range[1]), 'aoi'] = aoi

# Create 48 graphs (4 for each of the 12 emails)
for email_index in range(12):
    email_image_path = f"F:\\CODE\\pythonscripts\\FINAL\\Assets\\{email_images[email_index]}"
    start_time = start_times[email_index]
    end_time = end_times[email_index]
    df_email = df[(df['Unix Timestamp'] >= start_time) & (df['Unix Timestamp'] <= end_time)]

    # 1- Pupil Diameter over time
    plt.figure(figsize=(10, 6))
    plt.plot(df_email['Unix Timestamp'], df_email['Average pupil dilation'], label='Average Pupil Dilation')
    plt.xlabel('Time (s)')
    plt.ylabel('Pupil Diameter (mm)')
    plt.title(f'Pupil Diameter over Time - Email {email_index + 1}')
    plt.legend(loc='lower left')
    pupil_diameter_file = generate_unique_image_filename(save_dir, base_name=f"pupil_diameter_email_{email_index + 1}_", extension="png")
    plt.savefig(pupil_diameter_file)
    plt.close()

    # 2- Scatter Plot of Fixations
    fixations = df_email.dropna(subset=['Average eye position (pixels)'])
    fig, ax = plt.subplots(figsize=(10, 6))
    ax = plot_with_background(ax, email_image_path)
    sns.scatterplot(data=fixations, x=fixations['Average eye position (pixels)'].apply(lambda p: p[0]), 
                    y=fixations['Average eye position (pixels)'].apply(lambda p: p[1]), hue='aoi', ax=ax)
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    plt.legend(loc='lower left')
    plt.title(f'Scatter Plot of Fixations - Email {email_index + 1}')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    scatter_file = generate_unique_image_filename(save_dir, base_name=f"fixations_scatter_email_{email_index + 1}_", extension="png")
    plt.savefig(scatter_file)
    plt.close()

    # 3- Bar Chart of Fixations per AOI
    aoi_counts = df_email['aoi'].value_counts().reset_index()
    aoi_counts.columns = ['AOI', 'Count']

    plt.figure(figsize=(10, 6))
    sns.barplot(data=aoi_counts, x='AOI', y='Count')
    plt.title(f'Fixations per AOI - Email {email_index + 1}')
    plt.xlabel('Area of Interest')
    plt.ylabel('Count of Fixations')
    plt.xticks(rotation=0)
    # plt.legend(loc='lower left')
    aoi_file = generate_unique_image_filename(save_dir, base_name=f"fixations_per_aoi_email_{email_index + 1}_", extension="png")
    plt.savefig(aoi_file)
    plt.close()

    # 4- Scanpath Visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    ax = plot_with_background(ax, email_image_path)
    points = fixations[['Unix Timestamp', 'Average eye position (pixels)']]
    ax.plot(points['Average eye position (pixels)'].apply(lambda p: p[0]), 
            points['Average eye position (pixels)'].apply(lambda p: p[1]), '-o')

    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    plt.title(f'Scanpath Visualization - Email {email_index + 1}')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    scanpath_file = generate_unique_image_filename(save_dir, base_name=f"scanpath_email_{email_index + 1}_", extension="png")
    plt.savefig(scanpath_file)
    plt.close()

print("48 graphs created and saved successfully.")