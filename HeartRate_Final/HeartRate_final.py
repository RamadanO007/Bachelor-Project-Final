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

def calculate_ibis(timestamps):
    # Calculate IBIs (in seconds)
    ibis = [(timestamps[i] - timestamps[i-1]) for i in range(1, len(timestamps))]
    return ibis

def calculate_hrv_metrics(ibis):
    if len(ibis) < 2:
        return None, None
    sdnn = np.std(ibis)
    rmssd = np.sqrt(np.mean(np.square(np.diff(ibis))))
    return sdnn, rmssd

def save_heart_rate_data_with_hrv(heart_rate_data, output_dir):
    # Determine the next file number
    existing_files = [f for f in os.listdir(output_dir) if f.startswith("hr_data_hrv_") and f.endswith(".txt")]
    numbers = []
    for f in existing_files:
        try:
            number = int(f.split("_")[3].split(".")[0])
            numbers.append(number)
        except ValueError:
            continue
    
    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1

    output_file = os.path.join(output_dir, f"hr_data_hrv_{next_number}.txt")

    timestamps = [data[0] for data in heart_rate_data]
    ibis = calculate_ibis(timestamps)
    
    with open(output_file, 'w') as f:
        f.write("Timestamp\tHR\tSDNN\tRMSSD\n")
        for i in range(len(heart_rate_data)):
            timestamp, heart_rate = heart_rate_data[i]
            if i > 0 and i <= len(ibis):
                current_ibis = ibis[:i]
                sdnn, rmssd = calculate_hrv_metrics(current_ibis)
                if sdnn is not None and rmssd is not None:
                    f.write(f"{timestamp}\t{heart_rate}\t{sdnn:.4f}\t{rmssd:.4f}\n")
                else:
                    f.write(f"{timestamp}\t{heart_rate}\tN/A\tN/A\n")
            else:
                f.write(f"{timestamp}\t{heart_rate}\tN/A\tN/A\n")

    print(f"Heart rate data with HRV successfully saved to {output_file}")

# Path to your TCX file
tcx_file_path = r"F:\CODE\pythonscripts\FINAL\HeartRate_Final\Garmin_activities\activity_partic3.tcx"
output_dir = r"F:\CODE\pythonscripts\FINAL\HeartRate_Final\Raw Data"

# Verify the file path
if not os.path.isfile(tcx_file_path):
    print(f"File not found: {tcx_file_path}")
else:
    # Parse the TCX file and extract heart rate data
    heart_rate_data = parse_tcx(tcx_file_path)

    # Save the extracted heart rate data along with HRV metrics to a text file with a unique name
    if heart_rate_data:
        save_heart_rate_data_with_hrv(heart_rate_data, output_dir)
    else:
        print("No heart rate data extracted")
