import subprocess

# Get user input
user_number = input("Please enter the user number: ")
sequence = input("Please enter the sequence number (A to F): ")

# Paths to scripts
scripts = {
    "Mouse": r"F:\CODE\pythonscripts\FINAL\Mouse_Final\Graph_PlottingFinal.py",
    "HeartRate": r"F:\CODE\pythonscripts\FINAL\HeartRate_Final\Graph_PlottingFinal1.py",
    "EyeTracking": r"F:\CODE\pythonscripts\FINAL\Eye_Final\Graph_PlottingFinal1.py",
    "Keyboard": r"F:\CODE\pythonscripts\FINAL\KeyboardTracking_Final\Graph_PlottingFinal.py"
}

# Run scripts
processes = []

# Mouse, Heart Rate, and Eye Tracking need user number and sequence
for script_name in ["Mouse", "EyeTracking"]:
    processes.append(subprocess.Popen(["python", scripts[script_name], user_number, sequence]))

# Keyboard only needs user number
processes.append(subprocess.Popen(["python", scripts["Keyboard"], user_number]))
processes.append(subprocess.Popen(["python", scripts["HeartRate"], user_number]))


# Wait for all processes to complete
for p in processes:
    p.wait()

print("All scripts have been executed.")
