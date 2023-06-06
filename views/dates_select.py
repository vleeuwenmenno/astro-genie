import os
from tkinter import StringVar, Tk
import tkinter as tk
from utils.utils import calculateExposureTimes, formatExposureTime

from widgets.dates_select_widget import DatesSelector
from widgets.proceed_button_widget import ProceedButton

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
        self.objectList = DatesSelector(self, self.objectPath, label=f"Select dates for {selectedObject}", callback=self.objectListCallback)

        # Define a label to show exposure time and number of lights for selected dates
        self.detailsFrame = tk.LabelFrame(self, text="Details")
        self.selectedObjectLabel = tk.Label(self.detailsFrame, text=f"Selected object: {selectedObject}")
        self.exposureTimeLabel = tk.Label(self.detailsFrame, textvariable=self.exposureTime)
        self.numberOfLightsLabel = tk.Label(self.detailsFrame, textvariable=self.numberOfLights)

        # Pack widgets
        self.detailsFrame.pack(fill=tk.BOTH, padx=8, pady=8, expand=1)
        self.selectedObjectLabel.pack(fill=tk.BOTH, padx=8, pady=8, expand=1)
        self.exposureTimeLabel.pack(fill=tk.BOTH, padx=8, pady=8, expand=1)
        self.numberOfLightsLabel.pack(fill=tk.BOTH, padx=8, pady=8, expand=1)
        
        self.proceedBtn = ProceedButton(self, text="Proceed", command=self.proceedBtnClick, state=tk.DISABLED)
        self.backBtn = tk.Button(self, text="Back", command=self.backBtnClick)
        self.backBtn.pack(fill=tk.X, padx=8, pady=8, expand=1)

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