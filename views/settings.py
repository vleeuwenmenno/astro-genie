from tkinter import Tk
import tkinter as tk

from utils.settings import Settings


class SettingsWindow(Tk):
    def __init__(self):
        super().__init__()

        self.title("AstroGenie - Settings")
        self.geometry("920x200")
        self.iconbitmap("assets/icon.ico") # type: ignore
        self.attributes("-topmost", True)
        
        self.settings = Settings()
        self.settings.loadJson()

        # Dark sorcery is causing this to not update yet the settings are saved if we listen for the events
        self.dateFormat = tk.StringVar(self)
        self.badImagePrefix = tk.StringVar(self)
        self.defaultImageFolder = tk.StringVar(self)
        self.updateDefaultImageFolderOnLoad = tk.BooleanVar(self)

        self.dateFormat.set(self.settings.dateFormat)
        self.badImagePrefix.set(self.settings.badImagePrefix)
        self.defaultImageFolder.set(self.settings.defaultImageFolder)
        self.updateDefaultImageFolderOnLoad.set(self.settings.updateDefaultImageFolderOnLoad)
        
        self.defineSettingsWidgets()

    def defineSettingsWidgets(self):
        self.defineSettingsFrame()
        self.defineSettingsLabels()
        self.defineSettingsEntries()
        self.defineSettingsButtons()

    def defineSettingsFrame(self):
        self.settingsFrame = tk.LabelFrame(self, text="Settings", padx=8, pady=8)
        self.settingsFrame.pack()

    def defineSettingsLabels(self):
        self.dateFormatLabel = tk.Label(self.settingsFrame, text="Date Format: ")
        self.dateFormatLabel.grid(row=0, column=0, sticky="E")

        self.badImagePrefixLabel = tk.Label(self.settingsFrame, text="Bad Image Prefix: ")
        self.badImagePrefixLabel.grid(row=1, column=0, sticky="E")

        self.defaultImageFolderLabel = tk.Label(self.settingsFrame, text="Default Image Folder:")
        self.defaultImageFolderLabel.grid(row=2, column=0, sticky="E")

        self.updateDefaultImageFolderOnLoadLabel = tk.Label(self.settingsFrame, text="Update Default Image Folder when browsing:")
        self.updateDefaultImageFolderOnLoadLabel.grid(row=3, column=0, sticky="E")

    def defineSettingsEntries(self):
        self.dateFormatEntry = tk.Entry(self.settingsFrame, textvariable=self.dateFormat, width=50)
        self.dateFormatEntry.grid(row=0, column=1)

        self.dateFormatEntryHelpBtn = tk.Button(self.settingsFrame, text="?", command=lambda: tk.messagebox.showinfo("Date Format", "The date format is used to parse the date from the image folders. The default is %Y-%m-%d. For more examples, see https://strftime.org/."))
        self.dateFormatEntryHelpBtn.grid(row=0, column=2, padx=5)

        self.badImagePrefixEntry = tk.Entry(self.settingsFrame, textvariable=self.badImagePrefix, width=50)
        self.badImagePrefixEntry.grid(row=1, column=1)

        self.defaultImageFolderEntry = tk.Entry(self.settingsFrame, textvariable=self.defaultImageFolder, width=50)
        self.defaultImageFolderEntry.grid(row=2, column=1)

        self.updateDefaultImageFolderOnLoadCheckbutton = tk.Checkbutton(self.settingsFrame, variable=self.updateDefaultImageFolderOnLoad)
        self.updateDefaultImageFolderOnLoadCheckbutton.grid(row=3, column=1)

        # Checkbox event listener to write new value to settings class
        self.updateDefaultImageFolderOnLoadCheckbutton.bind("<Button-1>", self.onCheckboxClick)
                                                            
    def onCheckboxClick(self, event):
         # Dark sorcery is causing this to be negative instead of positive so we need to invert it
         self.settings.updateDefaultImageFolderOnLoad = not self.updateDefaultImageFolderOnLoad.get()

    def defineSettingsButtons(self):
        # Browse button for default image folder
        self.browseButton = tk.Button(self.settingsFrame, text="Browse", command=lambda: self.defaultImageFolder.set(tk.filedialog.askdirectory()))
        self.browseButton.grid(row=2, column=2, padx=5)

        self.buttonsFrame = tk.Frame(self.settingsFrame)

        self.cancelSettingsButton = tk.Button(self.buttonsFrame, text="Cancel", command=self.destroy)
        self.saveSettingsButton = tk.Button(self.buttonsFrame, text="Save & Close", command=lambda: [self.saveSettingsJson(), self.destroy()])
       
        # Grid aligned buttons to the bottom of the window
        self.buttonsFrame.grid(row=4, column=0, columnspan=2, sticky="E")
        self.cancelSettingsButton.grid(row=0, column=0, padx=5)
        self.saveSettingsButton.grid(row=0, column=1, padx=5)

    def saveSettingsJson(self):
        # Set the settings variables
        self.settings.dateFormat = self.dateFormat.get()
        self.settings.badImagePrefix = self.badImagePrefix.get()
        self.settings.defaultImageFolder = self.defaultImageFolder.get()

        # Save to settings class
        self.settings.saveJson()