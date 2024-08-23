from lxml import etree
import os
import datetime
import calendar
import numpy as np

def parse_tcx(file_path):
    ns = {
        'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
    }
    
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()
    except OSError as e:
        print(f"Error reading file '{file_path}': {e}")
        return []

    heart_rate_data = []

    for trackpoint in root.findall('.//tcx:Trackpoint', ns):
        time_elem = trackpoint.find('tcx:Time', ns)
        hr_elem = trackpoint.find('tcx:HeartRateBpm/tcx:Value', ns)

        if time_elem is not None and hr_elem is not None:
            time_str = time_elem.text
            time_obj = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            unix_timestamp = calendar.timegm(time_obj.utctimetuple()) + time_obj.microsecond / 1e6
            heart_rate = int(hr_elem.text)
            heart_rate_data.append((unix_timestamp, heart_rate))
    
    return heart_rate_data

def save_heart_rate_data(heart_rate_data, output_dir):
    # Determine the next file number
    existing_files = [f for f in os.listdir(output_dir) if f.startswith("hr_data_") and f.endswith(".txt")]
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

    output_file = os.path.join(output_dir, f"hr_data_{next_number}.txt")

    with open(output_file, 'w') as f:
        f.write("Timestamp, HR(bpm), HRV(ms), Resp(brpm)\n")
        for timestamp, heart_rate in heart_rate_data:
            f.write(f"{timestamp}, {heart_rate}, NaN, NaN\n")

    print(f"Heart rate data successfully saved to {output_file}")

# Path to your TCX file
tcx_file_path = r"F:\CODE\pythonscripts\FINAL\HeartRate_Final\Garmin_activities\activity_partic7.tcx"
output_dir = r"F:\CODE\pythonscripts\FINAL\HeartRate_Final\Raw Data"

# Verify the file path
if not os.path.isfile(tcx_file_path):
    print(f"File not found: {tcx_file_path}")
else:
    # Parse the TCX file and extract heart rate data
    heart_rate_data = parse_tcx(tcx_file_path)

    # Save the extracted heart rate data to a text file with a unique name
    if heart_rate_data:
        save_heart_rate_data(heart_rate_data, output_dir)
    else:
        print("No heart rate data extracted")
