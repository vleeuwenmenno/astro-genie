import tkinter as tk
import os
import datetime
import re
from tkinter import messagebox
import numpy as np

from PIL import ImageTk, Image, ImageEnhance
from astropy.io import fits

light_frames_selected = False
selected_dates_indices = []

def format_exposure_time(total_seconds):
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return f"{hours}h {minutes}m {seconds}s"

def create_select_date_window(selected_item, deep_sky_path):
    window = tk.Toplevel()
    window.title("Astro-Genie")
    window.geometry("1600x900")

    # Set the status bar text
    status_text_left = tk.StringVar()
    status_text_right = tk.StringVar()

    # Create the labels for the status bar
    status_bar = tk.Frame(window, bd=1, relief=tk.SUNKEN)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    left_status_label = tk.Label(status_bar, textvariable=status_text_left, bd=0, anchor=tk.W)
    left_status_label.pack(side=tk.LEFT, fill=tk.X, padx=(5, 0))

    right_status_label = tk.Label(status_bar, textvariable=status_text_right, bd=0, anchor=tk.E)
    right_status_label.pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))

    count_text = "Light Frames: 0"
    exposure_text = "Total Exposure: 0h 0m 0s"
    status_text_right.set(count_text + " | " + exposure_text)
    status_text_left.set("Selected Object: " + selected_item + " | Path: " + deep_sky_path)

    # Create a frame for the main window
    main_frame = tk.Frame(window)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create a frame for the dates list
    dates_frame = tk.Frame(main_frame, width=64)
    dates_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

    # Create a scrollbar for the dates list
    scrollbar = tk.Scrollbar(dates_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a listbox to display the dates
    date_listbox = tk.Listbox(dates_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
    date_listbox.pack(fill=tk.BOTH, expand=True)

    # Configure the scrollbar to work with the listbox
    scrollbar.config(command=date_listbox.yview)

    # Populate the date list
    object_path = os.path.join(deep_sky_path, selected_item)
    dates = [
        name for name in os.listdir(object_path)
        if os.path.isdir(os.path.join(object_path, name))
        and re.match(r"\d{2}-\d{2}-\d{4}$", name)
    ]
    dates = sorted(dates, key=lambda x: datetime.datetime.strptime(x, "%d-%m-%Y"))

    for date in dates:
        date_listbox.insert(tk.END, date)

    # Create a frame for the details container
    details_frame = tk.Frame(main_frame, width=0.6 * window.winfo_width())
    details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create a scrollbar for the light frames listbox
    light_frames_scrollbar = tk.Scrollbar(details_frame)
    light_frames_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a listbox to display the light frames
    light_frames_listbox = tk.Listbox(details_frame, selectmode=tk.SINGLE, yscrollcommand=light_frames_scrollbar.set)
    light_frames_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure the scrollbar to work with the light frames listbox
    light_frames_scrollbar.config(command=light_frames_listbox.yview)

    def load_light_frames():
        global light_frames_selected
        global selected_dates_indices

        # disable load_button and enable clear_button
        load_button.config(state=tk.DISABLED)
        clear_button.config(state=tk.NORMAL)
        open_calibration_window_btn.config(state=tk.NORMAL)
        proccess_window_btn.config(state=tk.NORMAL)
        togle_image_goodbad.config(state=tk.NORMAL)

        light_frames_selected = False

        # Clear the light frames list and image preview
        light_frames_listbox.delete(0, tk.END)
        image_label.configure(image='')

        # Disable the dates list
        date_listbox.config(state=tk.DISABLED)

        # Load the light frames
        selected_dates = date_listbox.curselection()
        selected_dates_indices = []
        for date_index in selected_dates:
            selected_dates_indices.append(date_index)

        total_lights = 0
        total_exposure_time = 0
        light_frames = []

        for index in selected_dates_indices:
            date = date_listbox.get(index)
            lights_path = os.path.join(object_path, date)

            # Handle inconsistent folder names
            possible_folders = ["Lights", "lights", "Light"]
            lights_folder = next(
                (f for f in possible_folders if os.path.isdir(os.path.join(lights_path, f))), None
            )

            if lights_folder:
                lights_folder_path = os.path.join(lights_path, lights_folder)
                if os.path.isdir(lights_folder_path):
                    # Check for sub-folders with exposure seconds
                    sub_folders = [
                        name for name in os.listdir(lights_folder_path)
                        if os.path.isdir(os.path.join(lights_folder_path, name))
                    ]

                    if sub_folders:
                        for sub_folder in sub_folders:
                            try:
                                exposure_seconds = float(sub_folder)
                            except ValueError:
                                continue

                            sub_folder_path = os.path.join(lights_folder_path, sub_folder)
                            light_files = [
                                os.path.join(sub_folder_path, name)
                                for name in os.listdir(sub_folder_path)
                                if os.path.isfile(os.path.join(sub_folder_path, name))
                            ]
                            light_frames.extend(light_files)
                            total_lights += len(light_files)
                            total_exposure_time += len(light_files) * exposure_seconds
                    else:
                        light_files = [
                            name
                            for name in os.listdir(lights_folder_path)
                            if os.path.isfile(os.path.join(lights_folder_path, name))
                        ]
                        total_lights += len(light_files)
                        light_frames.extend(light_files)

        # Update the status bar with the light frames count and total exposure time
        datasetsCount = str(len(selected_dates_indices))
        count_text = "Light Frames: " + str(total_lights)
        exposure_text = "Total Exposure: " + format_exposure_time(total_exposure_time)
        status_text_right.set("Selected datasets: " + datasetsCount + " | " + count_text + " | " + exposure_text)
        status_text_left.set("Selected Object: " + selected_item + " | Path: " + deep_sky_path)

        # Update the light frames listbox
        for frame in light_frames:
            light_frames_listbox.insert(tk.END, frame)

        # Select the first frame and show the image preview
        light_frames_listbox.selection_set(1)
        light_frames_listbox.activate(1)
        light_frames_listbox.see(1)
        show_image_preview(None)

    def update_status_bar(event=None, total_lights=0, total_exposure_time=0):

        # Update the status bar with the light frames count and total exposure time
        datasetsCount = str(len(selected_dates_indices))
        count_text = "Light Frames: " + str(total_lights)
        exposure_text = "Total Exposure: " + format_exposure_time(total_exposure_time)
        status_text_right.set( "Selected datasets: " + datasetsCount + " | " + count_text + " | " + exposure_text)
        status_text_left.set("Selected Object: " + selected_item + " | Path: " + deep_sky_path)

    def clear_light_frames():
        global light_frames_selected
        global selected_dates_indices

        # disable load_button and enable clear_button
        load_button.config(state=tk.NORMAL)
        clear_button.config(state=tk.DISABLED)
        togle_image_goodbad.config(state=tk.DISABLED)
        open_calibration_window_btn.config(state=tk.DISABLED)
        proccess_window_btn.config(state=tk.DISABLED)

        light_frames_selected = False
        selected_dates_indices = []

        # Clear the light frames list and image preview
        light_frames_listbox.delete(0, tk.END)
        image_label.configure(image='')

        # Enable the dates list
        date_listbox.config(state=tk.NORMAL)

        update_status_bar(total_lights=0, total_exposure_time=0)

    def update_details(event=None):
        global light_frames_selected
        global selected_dates_indices

        # Check if the event was triggered by the light frames listbox
        if light_frames_selected:
            light_frames_selected = False
            return

        selected_dates = date_listbox.curselection()
        selected_dates_indices = []
        for date_index in selected_dates:
            selected_dates_indices.append(date_index)

        total_lights = 0
        total_exposure_time = 0
        light_frames = []

        for index in selected_dates_indices:
            date = date_listbox.get(index)
            lights_path = os.path.join(object_path, date)

            # Handle inconsistent folder names
            possible_folders = ["Lights", "lights", "Light"]
            lights_folder = next(
                (f for f in possible_folders if os.path.isdir(os.path.join(lights_path, f))), None
            )

            if lights_folder:
                lights_folder_path = os.path.join(lights_path, lights_folder)
                if os.path.isdir(lights_folder_path):
                    # Check for sub-folders with exposure seconds
                    sub_folders = [
                        name for name in os.listdir(lights_folder_path)
                        if os.path.isdir(os.path.join(lights_folder_path, name))
                    ]

                    if sub_folders:
                        for sub_folder in sub_folders:
                            try:
                                exposure_seconds = float(sub_folder)
                            except ValueError:
                                continue

                            sub_folder_path = os.path.join(lights_folder_path, sub_folder)
                            light_files = [
                                os.path.join(sub_folder_path, name)
                                for name in os.listdir(sub_folder_path)
                                if os.path.isfile(os.path.join(sub_folder_path, name))
                            ]
                            light_frames.extend(light_files)
                            total_lights += len(light_files)
                            total_exposure_time += len(light_files) * exposure_seconds
                    else:
                        light_files = [
                            name
                            for name in os.listdir(lights_folder_path)
                            if os.path.isfile(os.path.join(lights_folder_path, name))
                        ]
                        total_lights += len(light_files)
                        light_frames.extend(light_files)

        update_status_bar(total_lights=total_lights, total_exposure_time=total_exposure_time)

    def show_image_preview(event):
        global light_frames_selected
        global selected_dates_indices

        light_frames_selected = True

        selected_frames = light_frames_listbox.curselection()
        if not selected_frames:
            return

        selected_frame_index = selected_frames[0]

        # Select the previous or next frame based on the pressed arrow key
        if event:
            if event.keysym == 'Left':
                selected_frame_index = (selected_frame_index - 1) % light_frames_listbox.size()
            elif event.keysym == 'Right':
                selected_frame_index = (selected_frame_index + 1) % light_frames_listbox.size()

        light_frames_listbox.selection_clear(0, tk.END)
        light_frames_listbox.selection_set(selected_frame_index)
        light_frames_listbox.activate(selected_frame_index)
        light_frames_listbox.see(selected_frame_index)

        image_path = light_frames_listbox.get(selected_frame_index)
        
        if os.path.isfile(image_path):
            with fits.open(image_path) as hdul:
                image_data = hdul[0].data

            # Normalize the image data
            image_data = (image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data))

            # Apply an auto-stretch to enhance visibility
            p_low, p_high = np.percentile(image_data, (1, 99))  # Adjust the percentiles as needed
            image_data = np.clip((image_data - p_low) / (p_high - p_low), 0, 1)

            # Convert the image data to a PIL Image
            image = Image.fromarray(np.uint8(image_data * 255), 'L')

            # Adjust the image size based on the window size
            image_size = min(window.winfo_width(), window.winfo_height())
            image = image.resize((image_size, image_size))

            photo = ImageTk.PhotoImage(image)

            # Update the image label
            image_label.configure(image=photo)
            image_label.image = photo
            
            # Call update_details() only if the event is not triggered by light_frames_listbox
            if event and event.widget != light_frames_listbox:
                update_details()

            # also add a check to see if the image is marked as bad
            file_name = os.path.basename(image_path)
            if file_name.startswith("BAD_"):
                togle_image_goodbad.config(text="Toggle Image as Good")
                marker_checkbox.select()
            else:
                togle_image_goodbad.config(text="Toggle Image as Bad")
                marker_checkbox.deselect()

        else:
            # Let's say the image is not found
            image_label.configure(image='')
            update_details()
            print("Image not found " + image_path)

    import select_calibration_window
    import process_window

    def close_window(window):
        window.withdraw()  # Hide the window
        window.master.deiconify()  # Show the main window

    def open_calibration_window():
        new_window = select_calibration_window.select_calibration_window(selected_item, deep_sky_path)
        new_window.protocol("WM_DELETE_WINDOW", lambda: close_window(new_window))
        window.iconify()

    def open_process_window():
        # Get all the selected dates from the listbox and selected_dates_indices
        dates = []
        for index in selected_dates_indices:
            dates.append(date_listbox.get(index))

        # Append the path of the selected object to dates
        dates = [os.path.join(object_path, date) for date in dates]

        new_window = process_window.proccess_window(selected_item, deep_sky_path, dates, []) # TODO: Pass through calibration frames
        new_window.protocol("WM_DELETE_WINDOW", lambda: close_window(new_window))
        window.iconify()
    
    def mark_current_image_as_bad():
        # Get the current image path
        selected_frames = light_frames_listbox.curselection()
        if not selected_frames:
            return
        
        for selected_frame_index in selected_frames:
            image_path = light_frames_listbox.get(selected_frame_index)
            file_name = os.path.basename(image_path)
            file_path = os.path.dirname(image_path)
            
            light_frames_listbox.delete(selected_frame_index)

            # Check if the image is already marked as bad
            if file_name.startswith("BAD_"):
                # Remove the "BAD_" prefix from the image file name
                os.rename(image_path, os.path.join(file_path, file_name[4:]))
                light_frames_listbox.insert(selected_frame_index, os.path.join(file_path, file_name[4:]))
            else:
                # Rename the image file to prefix it with "BAD_"
                os.rename(image_path, os.path.join(file_path, "BAD_" + file_name))
                light_frames_listbox.insert(selected_frame_index, os.path.join(file_path, "BAD_" + file_name))

            # Edit the listbox entry to reflect the change
            light_frames_listbox.selection_set(selected_frame_index)
        

    # Create a frame for the image preview
    image_frame = tk.Frame(main_frame, width=0.2 * window.winfo_width())
    image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create a frame for the buttons
    button_frame = tk.Frame(image_frame)
    button_frame.pack(side=tk.BOTTOM, pady=10)

    # Create a dates frame for the buttons
    dates_button_frame = tk.Frame(dates_frame)
    dates_button_frame.pack(side=tk.BOTTOM, pady=10)

    # Create a label for the image preview
    image_label = tk.Label(image_frame)
    image_label.pack(fill=tk.BOTH, expand=True)

    # Create the Clear button
    clear_button = tk.Button(dates_button_frame, text="Clear", command=clear_light_frames)
    clear_button.pack(side=tk.LEFT, padx=5)
    clear_button.config(state=tk.DISABLED)

    # Create the Load button
    load_button = tk.Button(dates_button_frame, text="Load Light Frames", command=load_light_frames)
    load_button.pack(side=tk.LEFT, padx=5)

    togle_image_goodbad = tk.Button(button_frame, text="Toggle Image as Good/Bad", command=mark_current_image_as_bad)
    togle_image_goodbad.pack(side=tk.LEFT, padx=5)
    togle_image_goodbad.config(state=tk.DISABLED)

    open_calibration_window_btn = tk.Button(button_frame, text="Select Calibration Frames", command=open_calibration_window)
    open_calibration_window_btn.pack(side=tk.LEFT, padx=5)
    open_calibration_window_btn.config(state=tk.DISABLED)

    proccess_window_btn = tk.Button(button_frame, text="Create Proccess Folder", command=open_process_window)
    proccess_window_btn.pack(side=tk.LEFT, padx=5)
    proccess_window_btn.config(state=tk.DISABLED)

    marker_checkbox = tk.Checkbutton(button_frame, text="Image is marked as bad", state=tk.DISABLED)
    marker_checkbox.pack(side=tk.LEFT, padx=5)

    # Bind the selection event of the listboxes to the respective functions
    light_frames_listbox.bind('<<ListboxSelect>>', show_image_preview)
    
    # Bind the left and right arrow key events to show the previous and next light frames
    light_frames_listbox.bind('<Left>', show_image_preview)
    light_frames_listbox.bind('<Right>', show_image_preview)
    
    # Bind spacebar to mark the current image as bad
    light_frames_listbox.bind('<space>', lambda event: mark_current_image_as_bad())

    return window
