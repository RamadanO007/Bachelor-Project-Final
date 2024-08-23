import os
import datetime
from garmin_fit_sdk import Decoder, Stream, Profile

# Define the path to the FIT file
fit_file_path = r"F:\CODE\pythonscripts\FINAL\HeartRate_Final\Garmin_activities\11.fit"

# Load the FIT file
stream = Stream.from_file(fit_file_path)
decoder = Decoder(stream)

filtered_messages = []

def mesg_listener(mesg_num, message):
    # Check if the message contains the required fields
    if 'current_stress' in message or 'heart_rate' in message or 'enhanced_respiration_rate' in message:
        # Save the message if it contains relevant data
        filtered_messages.append(message)

# Decode the FIT file with the custom mesg_listener
messages, errors = decoder.read(mesg_listener=mesg_listener)

if len(errors) > 0:
    print(f"Something went wrong decoding the file: {errors}")
else:
    # Prepare the text file content
    output_lines = ["Timestamp, HR(bpm), Stress(ms), Resp(brpm)"]
    
    for message in filtered_messages:
        # Convert timestamp to UNIX timestamp
        timestamp = message.get('timestamp', None)
        if timestamp:
            # Convert to offset-naive datetime by removing timezone info
            timestamp = timestamp.replace(tzinfo=None)
            unix_timestamp = int((timestamp - datetime.datetime(1970, 1, 1)).total_seconds())
        else:
            unix_timestamp = "NaN"

        # Get the heart rate, stress, and respiration values
        hr_value = message.get('heart_rate', "NaN")  # Replace 'NaN' with your default value if needed
        stress_value = message.get('current_stress', "NaN")  # Replace 'NaN' with your default value if needed
        respiration_value = message.get('enhanced_respiration_rate', "NaN")  # Replace 'NaN' with your default value if needed
        
        # Append the formatted line to the output list
        output_lines.append(f"{unix_timestamp}, {hr_value}, {stress_value}, {respiration_value}")

    # Determine the next file number
    save_directory = r"F:\CODE\pythonscripts\FINAL\HeartRate_Final\Raw Data"
    existing_files = [f for f in os.listdir(save_directory) if f.startswith("hr_data_") and f.endswith(".txt")]
    numbers = []
    for f in existing_files:
        try:
            number = int(f.split("_")[2].split(".")[0])
            numbers.append(number)
        except ValueError:
            continue
    
    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1

    # Create the output file path with the next available number
    output_file_name = f"hr_data_{next_number}.txt"
    output_file_path = os.path.join(save_directory, output_file_name)
    
    # Write the content to the text file
    with open(output_file_path, 'w') as f:
        for line in output_lines:
            f.write(line + "\n")

    print(f"Data successfully saved to {output_file_path}")
