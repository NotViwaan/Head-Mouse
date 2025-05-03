import threading
import tkinter as tk
import pythoncom
from eye_mouse_control import HeadControlledMouse  # Import your eye-controlled mouse script
from speech_typing import AssistiveApp  # Import your speech-controlled typing script
from PIL import Image, ImageTk  # Pillow for image handling

# Function to run the eye control script
def run_eye_control():
    HeadControlledMouse()

# Function to run the speech typing script
def run_speech_typing():
    pythoncom.CoInitialize()  # Initialize COM in the thread
    AssistiveApp()

# Function to start threads
def start_threads():
    # Create threads for each function
    eye_thread = threading.Thread(target=run_eye_control)
    speech_thread = threading.Thread(target=run_speech_typing)

    # Start both threads
    eye_thread.start()
    speech_thread.start()

# Function to cycle through colors
def cycle_button_color():
    global color_index
    color = colors[color_index]  # Get the current color
    start_button.config(bg=color)  # Change the button background color
    color_index = (color_index + 1) % len(colors)  # Update index for next color
    start_button.after(300, cycle_button_color)  # Schedule next color change

# Function to load and display background image
def load_background_image(root):
    bg_image = Image.open("C:/Users/M S I/Desktop/head mouse 11/Head Mouse/logo.png")  # Change to your image file path
    bg_image = bg_image.resize((300, 150), Image.LANCZOS)  # Resize image to fit
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(root, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.pack(pady=(10, 0))  # Add some padding on top

def create_ui():
    # Create the main window
    root = tk.Tk()
    root.title("Control Panel")
    root.geometry("300x250")  # Increased height for the image and button
    root.configure(bg="#333333")  # Dark background

    # Load and display background image
    load_background_image(root)

    # Create the start button
    global start_button
    start_button = tk.Button(root, text="Start", command=start_threads, bg='#555555', fg='white', font=('Helvetica', 12))
    start_button.pack(pady=20)

    # Start cycling button colors
    cycle_button_color()

    # Start the Tkinter event loop
    root.mainloop()

# Color list for cycling
colors = ['#FF5733', '#FF8D33', '#FFCC33', '#8DFF33', '#33FF57', '#33FF8D', '#33CCFF', '#337BFF', '#3356FF', '#5A33FF', '#A933FF', '#FF33B5']
color_index = 0  # Initialize color index

if __name__ == "__main__":
    create_ui()
