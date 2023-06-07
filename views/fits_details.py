from tkinter import Tk, Label, BOTH, Scrollbar, Canvas
import tkinter as tk

class FitsDetailsWindow(Tk):
    def __init__(self):
        super().__init__()

        self.title("FITS Details")
        self.geometry("630x600")
        self.fitsHeader = ""

        # Frame with label and FITs details
        self.frm_fits_details = tk.LabelFrame(self, text="FITS Details")
        self.frm_fits_details.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas for the scrollable part
        self.canvas = Canvas(self.frm_fits_details)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        self.scrollbar = Scrollbar(self.frm_fits_details, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame inside the canvas
        self.inner_frame = tk.Frame(self.canvas)
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Add inner frame to canvas
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind mousewheel scroll to canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def format_fits_details(self, details):
        # Remove leading and trailing white spaces
        details = details.strip()

        # Split the string into lines by "/"
        lines = details.split(" / ")

        # Create a dictionary
        fits_dict = {}

        # Iterate over lines and split each line by "=" to get key-value pairs
        for line in lines:
            if "=" in line:
                key, value = line.split("=", 1)  # Split by the first "="
                # Remove leading and trailing white spaces from key and value
                key = key.strip()
                value = value.strip()

                # Add the key-value pair to the dictionary
                fits_dict[key] = value

        return fits_dict

    def clear_frame(self):
        # Destroy all widgets in the frame
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

    def refresh(self):
        # Clear the frame
        self.clear_frame()

        # Let's make the fitsHeader string and add new lines to it
        fits_dict = self.format_fits_details(str(self.fitsHeader))

        for i, (key, value) in enumerate(fits_dict.items()):
            lbl_key = tk.Label(self.inner_frame, text=key, anchor="w")
            lbl_value = tk.Label(self.inner_frame, text=value, anchor="e")
            lbl_key.grid(row=i, column=0, sticky="w")
            lbl_value.grid(row=i, column=1, sticky="e")

        self.update()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
