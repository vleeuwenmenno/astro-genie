import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Global variable for the history file path
history_file_path = "history.txt"

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        deep_sky_path.set(folder_path)
        save_path_to_history(folder_path)
        populate_object_list(folder_path)

def save_path_to_history(folder_path):
    try:
        with open(history_file_path, "w") as file:
            file.write(folder_path)
    except IOError:
        messagebox.showerror("Error", "Failed to save path to history file.")

def load_path_from_history():
    if os.path.exists(history_file_path):
        try:
            with open(history_file_path, "r") as file:
                folder_path = file.read()
                if folder_path:
                    deep_sky_path.set(folder_path)
                    populate_object_list(folder_path)
        except IOError:
            messagebox.showerror("Error", "Failed to load path from history file.")

def populate_object_list(folder_path):
    object_list.delete(0, tk.END)  # Clear existing object list
    objects = [
        name for name in os.listdir(folder_path) if any(
            catalog in name for catalog in ["M ", "NGC ", "IC "]
        )
    ]
    for obj in objects:
        object_list.insert(tk.END, obj)

import select_date_window

def close_window(window):
    window.withdraw()  # Hide the window
    window.master.deiconify()  # Show the main window

def open_next_window():
    selected_item = object_list.get(tk.ACTIVE)
    if selected_item:
        new_window = select_date_window.create_select_date_window(selected_item, deep_sky_path.get())
        new_window.protocol("WM_DELETE_WINDOW", lambda: close_window(new_window))
        window.iconify()  # Minimize the main window
    else:
        messagebox.showinfo("Error", "No object selected")


def update_next_button_state(event):
    if object_list.curselection():
        next_button.config(state=tk.NORMAL)
    else:
        next_button.config(state=tk.DISABLED)

# Create the main window
window = tk.Tk()
window.title("Astro-Genie")
window.geometry("400x500")

# Create a label frame to hold the folder path label and browse button
path_label_frame = tk.LabelFrame(window, text="Deep-Sky Folder Path")
path_label_frame.pack(fill=tk.BOTH, padx=10, pady=10)

# Create a label to display the Deep-Sky folder path
deep_sky_path = tk.StringVar()
deep_sky_path_label = tk.Label(path_label_frame, textvariable=deep_sky_path, anchor="w")
deep_sky_path_label.pack(side=tk.LEFT, padx=(10, 0))

# Create a button to browse for the Deep-Sky folder
browse_button = tk.Button(path_label_frame, text="Browse", command=browse_folder)
browse_button.pack(side=tk.RIGHT, padx=(0, 10), pady=4)

# Create a label for the object list
object_list_label = tk.Label(window, text="Objects:")
object_list_label.pack()

# Create a listbox to display the objects
object_list = tk.Listbox(window)
object_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create a Next button
next_button = tk.Button(window, text="Next", state=tk.DISABLED, command=open_next_window)
next_button.pack(pady=10)
next_button.config(width=10, height=2)

# Variables to store the object list data
object_list_data = []

# Update the object list and enable/disable the Next button
def update_object_list():
    object_list_data = object_list.get(0, tk.END)
    update_next_button_state(None)

# Bind the selection and click events to update the Next button and populate the filtered object list
object_list.bind("<<ListboxSelect>>", update_next_button_state)
object_list.bind("<ButtonRelease-1>", update_next_button_state)

# Call the function to load the path from the history file
load_path_from_history()

import ctypes
import sys

def run_as_admin():
    if sys.platform.startswith("win"):
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except Exception as e:
            print(e)
            sys.exit(1)
    else:
        print("Admin rights not supported on this platform.")
        sys.exit(1)

# Check if the current script is running with admin rights
if ctypes.windll.shell32.IsUserAnAdmin():
    # Run the main event loop
    window.mainloop()
else:
    # Re-run the script with elevated privileges
    run_as_admin()