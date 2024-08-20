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

# Directories
input_file = f"F:\\CODE\\pythonscripts\\FINAL\\Mouse_Final\\Raw Data\\mouse_t_{user_number}.txt"
timestamps_file = f"F:\\CODE\\pythonscripts\\FINAL\\MASTER_SCRIPT\\Assets\\timestamps_{user_number}.txt"
save_dir = f"F:\\CODE\\pythonscripts\\FINAL\\Mouse_Final\\Graph_CSV\\participant_{user_number}"

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
def generate_unique_image_filename(directory, base_name="mouse_graph_", extension="png"):
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

# Adjust the needed area of mouse tracking
screen_x_start = 1920  # Start X coordinate of the area
screen_y_start = -634  # Start Y coordinate of the area


# screen_y_start = -634  # Start Y coordinate of the area

screen_x_end = 3600    # End X coordinate of the area
screen_y_end = 415     # End Y coordinate of the area

# screen_y_end = 415     # End Y coordinate of the area

# Read the raw mouse data
data = []
with open(input_file, 'r') as file:
    for line in file:
        timestamp, event_data = line.split(',', 1)
        event_data = event_data.strip().replace('true', 'True').replace('false', 'False')
        event_data = eval(event_data)
        event_data['timestamp'] = float(timestamp.split(': ')[1])
        # Filter for the specified screen area
        if screen_x_start <= event_data['x'] < screen_x_end and \
           screen_y_start <= event_data['y'] < screen_y_end:
            event_data['x'] -= screen_x_start
            event_data['y'] -= screen_y_start
            data.append(event_data)

# Convert to DataFrame
df = pd.DataFrame(data)

# Save the raw data to CSV
raw_data_file = generate_unique_image_filename(save_dir, base_name="raw_mouse_data_", extension="csv")
df.to_csv(raw_data_file, index=False)

# Define AOIs based on specific parts of the email
aoi_definitions = {
    'Sender Email': {'x_range': (460, 710), 'y_range': (255, 300)},
    'Email Header': {'x_range': (460, 1630), 'y_range': (330, 440)},
    'Main Content': {'x_range': (448, 1680), 'y_range': (440, 739)},
    'Footer': {'x_range': (450, 1680), 'y_range': (740, 1000)},
    'Inbox and Folders': {'x_range': (145, 440), 'y_range': (170, 645)},
}

# Assign AOIs to mouse events
df['aoi'] = 'Other'
for aoi, coords in aoi_definitions.items():
    x_range, y_range = coords['x_range'], coords['y_range']
    df.loc[(df['x'] >= x_range[0]) & (df['x'] < x_range[1]) & 
           (df['y'] >= y_range[0]) & (df['y'] < y_range[1]), 'aoi'] = aoi

# Create 48 graphs (4 for each of the 12 emails)
for email_index in range(12):
    email_image_path = f"F:\\CODE\\pythonscripts\\FINAL\\Assets\\{email_images[email_index]}"
    start_time = start_times[email_index]
    end_time = end_times[email_index]
    df_email = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]

    # 1- Scatter Plot of Clicks with email image background
    click_data = df_email[df_email['type'] == 'click']
    fig, ax = plt.subplots(figsize=(10, 6))
    ax = plot_with_background(ax, email_image_path)
    sns.scatterplot(data=click_data, x='x', y='y', hue='button', style='pressed', markers=True, ax=ax)
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    plt.legend(loc='lower left')
    plt.title(f'Mouse Clicks Scatter Plot - Email {email_index + 1}')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    scatter_file = generate_unique_image_filename(save_dir, base_name=f"mouse_clicks_scatter_email_{email_index + 1}_", extension="png")
    plt.savefig(scatter_file)
    plt.close()

    # 2- AOI Analysis with Bar Plot
    aoi_counts = df_email['aoi'].value_counts().reset_index()
    aoi_counts.columns = ['AOI', 'Count']

    plt.figure(figsize=(10, 6))
    sns.barplot(data=aoi_counts, x='AOI', y='Count')
    plt.title(f'AOI Analysis (Count of All Mouse Events) - Email {email_index + 1}')
    plt.xlabel('Area of Interest')
    plt.ylabel('Count of Mouse Events')
    plt.xticks(rotation=0)
    aoi_file = generate_unique_image_filename(save_dir, base_name=f"mouse_aoi_analysis_email_{email_index + 1}_", extension="png")
    plt.savefig(aoi_file)
    plt.close()

    # 3- Summarize data per AOI
    aoi_summary = df_email.groupby('aoi').agg({
        'timestamp': ['min', 'max'],
        'x': ['count', 'mean'],
        'y': ['count', 'mean']
    }).reset_index()
    aoi_summary.columns = ['AOI', 'First_Timestamp', 'Last_Timestamp', 'X_Count', 'X_Mean', 'Y_Count', 'Y_Mean']
    aoi_summary_file = generate_unique_image_filename(save_dir, base_name=f"aoi_summary_email_{email_index + 1}_", extension="csv")
    aoi_summary.to_csv(aoi_summary_file, index=False)

    # 4- Heatmap of Mouse Movements
    heatmap_data = df_email[df_email['type'] == 'move']
    heatmap, xedges, yedges = np.histogram2d(heatmap_data['x'], heatmap_data['y'], bins=(50, 50), range=[[0, 1680], [0, 1000]])

    fig, ax = plt.subplots()
    ax = plot_with_background(ax, email_image_path)
    cax = ax.imshow(heatmap.T, origin='upper', cmap='hot', interpolation='nearest', alpha=0.6, extent=[0, 1680, 1000, 0])
    cbar = fig.colorbar(cax)
    cbar.set_label('Number of Movements')
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    plt.title(f'Heatmap of Mouse Movements - Email {email_index + 1}')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    heatmap_file = generate_unique_image_filename(save_dir, base_name=f"mouse_movements_heatmap_email_{email_index + 1}_", extension="png")
    plt.savefig(heatmap_file)
    plt.close()

print("48 graphs created and saved successfully.")
