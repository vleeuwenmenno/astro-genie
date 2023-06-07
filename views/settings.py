import json
from tkinter import Tk
import tkinter as tk

from utils.settings import Settings


class SettingsWindow(Tk):
    def __init__(self):
        super().__init__()

        # Window can spawn at the center of the screen
        self.eval('tk::PlaceWindow . center')

        self.title("AstroGenie - Settings")
        self.geometry("340x400")
        self.iconbitmap("assets/icon.ico") # type: ignore
        
        self.dateFormat = tk.StringVar()
        self.badImagePrefix = tk.StringVar()
        
        self.defineSettingsWidgets()

        self.settings = Settings()
        self.loadSettingsJson()

    def defineSettingsWidgets(self):
        self.defineSettingsFrame()
        self.defineSettingsLabels()
        self.defineSettingsEntries()
        self.defineSettingsButtons()

    def defineSettingsFrame(self):
        self.settingsFrame = tk.Frame(self)
        self.settingsFrame.pack()

    def defineSettingsLabels(self):
        self.dateFormatLabel = tk.Label(self.settingsFrame, text="Date Format: ")
        self.dateFormatLabel.grid(row=0, column=0, sticky="E")

        self.badImagePrefixLabel = tk.Label(self.settingsFrame, text="Bad Image Prefix: ")
        self.badImagePrefixLabel.grid(row=1, column=0, sticky="E")

    def defineSettingsEntries(self):
        self.dateFormatEntry = tk.Entry(self.settingsFrame, textvariable=self.dateFormat)
        self.dateFormatEntry.grid(row=0, column=1)

        self.badImagePrefixEntry = tk.Entry(self.settingsFrame, textvariable=self.badImagePrefix)
        self.badImagePrefixEntry.grid(row=1, column=1)

    def defineSettingsButtons(self):
        self.saveSettingsButton = tk.Button(self.settingsFrame, text="Save", command=self.saveSettingsJson)
        self.saveSettingsButton.grid(row=2, column=0, sticky="E")

        self.cancelSettingsButton = tk.Button(self.settingsFrame, text="Cancel", command=self.destroy)
        self.cancelSettingsButton.grid(row=2, column=1, sticky="W")

    def loadSettingsJson(self):
        # Load from settings class
        self.settings.loadJson()

        # Set the settings variables
        self.dateFormat.set(self.settings.dateFormat)
        self.badImagePrefix.set(self.settings.badImagePrefix)

    def saveSettingsJson(self):
        # Set the settings variables
        self.settings.dateFormat = self.dateFormat.get()
        self.settings.badImagePrefix = self.badImagePrefix.get()

        # Save to settings class
        self.settings.saveJson()