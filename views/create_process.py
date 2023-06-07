import os
from tkinter import Tk
import tkinter as tk
import shutil
from tkinter import filedialog, messagebox

from utils.utils import calculateExposureTimes, formatExposureTime

open_process_button = None

# Define function to create frame with label
def createFrameWithLabel(window, text, label):
    # Create a label frame to hold the folder path label and browse button
    frame = tk.LabelFrame(window, text=label)
    frame.pack(fill=tk.BOTH, padx=10, pady=10)

    # Create a label to display the process folder path
    frame_label = tk.Label(frame, textvariable=text, anchor="w")
    frame_label.pack(side=tk.LEFT, padx=(10, 0))

    return frame

class CreateProcessWindow(Tk):
    def __init__(self, selectedDates, objectPath, selectedObject):

        self.title("AstroGenie - Create process")
        self.geometry("700x380")        
        self.iconbitmap("assets/icon.ico") # type: ignore

        process_folder_path = tk.StringVar()

        total_lights, total_exposure_time, lightFramePaths = calculateExposureTimes(selectedDates, objectPath)

        def openFolder(folder_path):
            if os.path.isdir(folder_path):
                os.startfile(folder_path)
                return

            # Enable the process button
            process_button.config(state=tk.NORMAL)
            
            global open_process_button

            if open_process_button:
                open_process_button.destroy()

        def clearProcessFolder(process_folder_path):
            # Recursively delete the process folder
            if os.path.isdir(process_folder_path):
                shutil.rmtree(process_folder_path)

            # Create new process folder if it doesn't exist
            if not os.path.isdir(process_folder_path):
                os.mkdir(process_folder_path)

        def createProcessFolder(selected_dates, process_folder_path, filter_prefix, prefix):
            total_lights, total_exposure_time, lightFramePaths = calculateExposureTimes(selectedDates, objectPath)

            # Check that process folder path is valid
            if not os.path.isdir(process_folder_path):
                os.mkdir(process_folder_path)
                        
            # Make sure the folder is empty
            if os.listdir(process_folder_path):
                return

            # Index all light files in selected_dates
            print(str(len(lightFramePaths)) + " light frames found")

            # Index all calibration files in selected_calibrations
            # TODO : Add support for darks, flats, and bias

            # If filter is checked, remove any frames with the prefix
            if filter_prefix:
                print("Filtering prefixed frames")
                lightFramePaths = [light_frame for light_frame in lightFramePaths if not os.path.basename(light_frame).startswith(prefix)]

            # Create light folder
            print("Creating light folder")
            light_folder_path = os.path.join(process_folder_path, "Lights")
            os.mkdir(light_folder_path)

            # Create symlinks to light frames
            print("Creating links to light frames")
            for light_frame in lightFramePaths:
                if filter_prefix and os.path.basename(light_frame).startswith(prefix):
                    print("Skipping " + os.path.basename(light_frame))
                    continue

                # if hardlinks is checked make sure the source file is on the same drive as the process folder
                if hardlinks.get() and os.path.splitdrive(light_frame)[0] != os.path.splitdrive(process_folder_path)[0]:
                    messagebox.showerror("Error", "Hardlinks can only be created on the same drive as the process folder")
                    clearProcessFolder(process_folder_path)
                    return
                
                if copy.get():
                    print("Copying " + os.path.basename(light_frame))
                    try:
                        shutil.copy(light_frame, os.path.join(light_folder_path, os.path.basename(light_frame)))
                    except OSError as e:
                        messagebox.showerror("Error", "Failed to copy " + os.path.basename(light_frame))
                        clearProcessFolder(process_folder_path)
                        return
                    continue
                else:
                    # Let's try to create the link
                    try:
                        if hardlinks.get():
                            print("Creating hardlink for " + os.path.basename(light_frame))
                            os.link(light_frame, os.path.join(light_folder_path, os.path.basename(light_frame)))
                        else:
                            print("Creating symlink for " + os.path.basename(light_frame))
                            os.symlink(light_frame, os.path.join(light_folder_path, os.path.basename(light_frame)))
                    except OSError as e:
                        messagebox.showerror("Error", "Failed to create link for " + os.path.basename(light_frame) + "\n\nMake sure the process folder is on the same drive as the source files when creatng hardlinks and keep note that exFAT and FAT32 file systems do not support symlinks.")
                        clearProcessFolder(process_folder_path)
                        return

            # Create folders for each calibration type
            print("Creating calibration folders")
            # TODO : Add support for darks, flats, and bias

            # Create symlinks to calibration frames'
            print("Creating symlinks to calibration frames")
            # TODO : Add support for darks, flats, and bias

            messagebox.showinfo("Success", "Process folder created successfully")
            
            # Spawn a new button to open the process folder
            global open_process_button
            open_process_button = tk.Button(self, text="Open Process Folder", command=lambda: openFolder(process_folder_path))
            open_process_button.pack(pady=10)
            open_process_button.config(width=30, height=2)

            # Disable the process button
            process_button.config(state=tk.DISABLED)

        def browseFolder():
            folder_path = filedialog.askdirectory()
            if folder_path:
                process_folder_path.set(folder_path)

                if os.path.isdir(folder_path) and not os.listdir(folder_path):
                    process_button.config(state=tk.NORMAL)
                else:
                    process_button.config(state=tk.DISABLED)
        
        def toggleCopy():
            hardlinks_checkbox.deselect()
            if copy.get():
                hardlinks_checkbox.config(state=tk.DISABLED)
            else:
                hardlinks_checkbox.config(state=tk.NORMAL)

        def togglePrefixEntry():
            if filter_prefix.get():
                prefix_entry.config(state=tk.NORMAL)
            else:
                prefix_entry.config(state=tk.DISABLED)

        # Create labels to display the selected object, deep-sky path, dates, and calibrations
        selected_object_label = tk.Label(self, text="Selected Object: " + selectedObject)
        selected_object_label.pack()

        # Create label to show expected exposure time
        exposure_time = tk.StringVar()
        exposure_time.set("Expected Exposure Time: " + formatExposureTime(total_exposure_time) + " (" + str(total_lights) + " lights)")
        exposure_time_label = tk.Label(self, textvariable=exposure_time)
        exposure_time_label.pack()
        
        # Create a label frame to hold the folder path label and browse button
        path_label_frame = createFrameWithLabel(self, process_folder_path, "Process Folder Path")

        # Create a button to browse for the process folder
        browse_button = tk.Button(path_label_frame, text="Browse", command=browseFolder)
        browse_button.pack(side=tk.RIGHT, padx=(0, 10), pady=4)

        # Create a label frame to hold the folder path label and browse button
        paths = tk.StringVar()
        paths.set("\n".join(selectedDates))
        frame = createFrameWithLabel(self, paths, "Light Frame Paths ("+str(len(selectedDates))+")")

        optionFrame = createFrameWithLabel(self, None, "Options")

        # Create checkbox for filitering any prefixed frames
        filter_prefix = tk.BooleanVar()
        filter_prefix.set(True)
        filter_prefix_checkbox = tk.Checkbutton(optionFrame, text="Filter prefixed frames", variable=filter_prefix)
        filter_prefix_checkbox.pack(side=tk.LEFT, padx=(0, 10), pady=4)

        # Define the prefix to filter
        prefix = tk.StringVar()
        prefix.set("BAD_")
        prefix_entry = tk.Entry(optionFrame, textvariable=prefix)
        prefix_entry.pack(side=tk.LEFT, padx=(0, 10), pady=4)

        # Checkbox for hardlinks instead of symlinks
        hardlinks = tk.BooleanVar()
        hardlinks.set(False)
        hardlinks_checkbox = tk.Checkbutton(optionFrame, text="Use hardlinks instead of symlinks", variable=hardlinks)
        hardlinks_checkbox.pack(side=tk.LEFT, padx=(0, 10), pady=4)

        # Checkbox for copying instead of linking
        copy = tk.BooleanVar()
        copy.set(False)
        copy_checkbox = tk.Checkbutton(optionFrame, text="Copy instead of linking", variable=copy)
        copy_checkbox.pack(side=tk.LEFT, padx=(0, 10), pady=4)

        copy_checkbox.config(command=toggleCopy)
        filter_prefix_checkbox.config(command=togglePrefixEntry)

        # Create a button to process the images
        process_button = tk.Button(self, text="Create Process Folder", command=lambda: createProcessFolder(selectedDates, process_folder_path.get(), filter_prefix.get(), prefix.get()))
        process_button.pack(pady=10)
        process_button.config(width=30, height=2)
        process_button.config(state=tk.DISABLED)

        return self
