import os
from tkinter import Tk
import tkinter as tk
from utils.utils import calculateExposureTimes, formatExposureTime

from widgets.dates_select_widget import DatesSelector
from views.light_frames_inspect import LightFramesInspectWindow

class DatesSelectWindow(Tk):
    def __init__(self, objectsPath:str, selectedObject:str):
        super().__init__()

        # Window can spawn at the center of the screen
        self.eval('tk::PlaceWindow . center')
        
        self.title("AstroGenie - Select dates")
        self.geometry("340x400")
        self.iconbitmap("assets/icon.ico") # type: ignore

        self.objectsPath = objectsPath
        self.selectedObject = selectedObject
        self.objectPath = tk.StringVar()

        self.exposureTime = tk.StringVar()
        self.numberOfLights = tk.StringVar()
        self.objectPath.set(os.path.join(objectsPath, selectedObject))
        self.selectedDates = []       

        # Define widgets
        self.objectListFrame = tk.Frame(self)
        self.objectList = DatesSelector(self.objectListFrame, self.objectPath, label=f"Select dates for {selectedObject}", callback=self.objectListCallback)

        # Define labels
        self.detailsFrame = tk.LabelFrame(self, text="Details")
        self.selectedObjectLabel = tk.Label(self.detailsFrame, text=f"Selected object: {selectedObject}")
        self.exposureTimeLabel = tk.Label(self.detailsFrame, textvariable=self.exposureTime)
        self.numberOfLightsLabel = tk.Label(self.detailsFrame, textvariable=self.numberOfLights)

        # Buttons frame
        self.buttonFrame = tk.Frame(self)
        self.buttonFrame.columnconfigure(0, weight=1)
        self.buttonFrame.columnconfigure(2, weight=1)

        # Define buttons
        self.proceedBtn = tk.Button(self.buttonFrame, text="Proceed", command=self.proceedBtnClick, state=tk.DISABLED)
        self.backBtn = tk.Button(self.buttonFrame, text="Back", command=self.backBtnClick)

        self.backBtn.grid(row=0, column=1, padx=8, pady=8)
        self.proceedBtn.grid(row=0, column=2, padx=8, pady=8)
        self.buttonFrame.grid(row=2, column=0, padx=8, pady=8, sticky=tk.W+tk.E)

        # Grid detail labels
        self.selectedObjectLabel.grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        self.exposureTimeLabel.grid(row=1, column=0, padx=8, pady=8, sticky=tk.W)
        self.numberOfLightsLabel.grid(row=2, column=0, padx=8, pady=8, sticky=tk.W)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Grid frames
        self.objectListFrame.grid(row=0, column=0, padx=8, pady=8, sticky=tk.N+tk.S+tk.E+tk.W)
        self.detailsFrame.grid(row=1, column=0, padx=8, pady=8, sticky=tk.W+tk.E)

    def backBtnClick(self):
        self.destroy()
        import views.object_select as objects_select
        objects_select.ObjectSelectWindow()
        pass

    def objectListCallback(self, selectedItems:list):
        self.selectedDates = selectedItems

        # Calculate exposure time and number of lights
        total_lights, total_exposure_time, light_frames = calculateExposureTimes(selectedItems, self.objectPath.get())

        # Update labels
        self.exposureTime.set(f"Exposure time: {formatExposureTime(total_exposure_time)}")
        self.numberOfLights.set(f"Number of lights: {total_lights}")

        if selectedItems != "":
            self.proceedBtn.config(state=tk.NORMAL)
        else:
            self.proceedBtn.config(state=tk.DISABLED)

    def proceedBtnClick(self):
        self.destroy()
        LightFramesInspectWindow(self.objectPath.get(), self.selectedObject, self.selectedDates)
        pass