from pynput import mouse
import json
import time
import os

# List to store mouse events
mouse_data = []

# Variable to control when to start saving data
start_recording = False

# Directory to save the files
save_dir = "F:\\CODE\\pythonscripts\\FINAL\\Mouse_Final\\Raw Data"

# Ensure the directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
print(f"Text files will be saved to: {save_dir}")

# Function to determine the next file name for txt files
def get_next_txt_file_name():
    files = [f for f in os.listdir(save_dir) if f.startswith("mouse_t_") and f.endswith(".txt")]
    max_index = 0
    for file in files:
        try:
            index = int(file.split("_")[-1].split(".")[0])
            if index > max_index:
                max_index = index
        except ValueError:
            continue
    return f"mouse_t_{max_index + 1}.txt"

# Callback function to capture mouse move events
def on_move(x, y):
    if start_recording:
        event = {
            'type': 'move',
            'x': x,
            'y': y,
            'timestamp': time.time()
        }
        mouse_data.append(event)
        print(event)  # Print event to console

# Callback function to capture mouse click events
def on_click(x, y, button, pressed):
    if start_recording:
        event = {
            'type': 'click',
            'x': x,
            'y': y,
            'button': str(button),
            'pressed': pressed,
            'timestamp': time.time()
        }
        mouse_data.append(event)
        print(event)  # Print event to console

# Callback function to capture mouse scroll events
def on_scroll(x, y, dx, dy):
    if start_recording:
        event = {
            'type': 'scroll',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'timestamp': time.time()
        }
        mouse_data.append(event)
        print(event)  # Print event to console

# Function to save mouse data to a file
def save_data():
    txt_save_path = os.path.join(save_dir, get_next_txt_file_name())
    print(f"Saving mouse data to: {txt_save_path}")  # Debug print statement
    with open(txt_save_path, 'w') as f:  # Use 'w' to write a new file
        for event in mouse_data:
            timestamp = event.pop('timestamp')
            event_str = json.dumps(event)
            formatted_event = f"Timestamp: {timestamp}, {event_str}"
            f.write(f"{formatted_event}\n")
    return txt_save_path

# Main function to start the listener and handle user input
def main():
    global start_recording, mouse_data

    listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll
    )

    listener.start()
    print("Type 's' to begin recording mouse events, 'e' to end recording and save the file, and 'q' to exit the program.")

    while True:
        user_input = input()
        if user_input.lower() == 's':
            start_recording = True
            print("Started recording mouse events.")
        elif user_input.lower() == 'e':
            start_recording = False
            print("Stopped recording mouse events.")
            txt_save_path = save_data()
            print(f"Mouse data saved to {txt_save_path}")
            mouse_data = []  # Clear mouse data after saving
        elif user_input.lower() == 'q':
            listener.stop()
            listener.join()
            print("Exiting the program.")
            break
        else:
            print("Invalid command. Type 's' to begin recording, 'e' to end recording and save the file, and 'q' to exit the program.")

if __name__ == "__main__":
    main()
