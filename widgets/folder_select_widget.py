import tkinter as tk
from tkinter import filedialog

class FolderSelector:
    def __init__(self, window, label:str="", buttonLabel:str="Browse", callback=None) -> None:
        self.selectedPath = tk.StringVar()
        self.frame = tk.LabelFrame(window, text=label)
        self.selectedPathLabel = tk.Label(self.frame, textvariable=self.selectedPath, anchor="w")
        self.browse_button = tk.Button(self.frame, text=buttonLabel, command=self.browseFolder)
        self.callback = callback

        self.frame.pack(fill=tk.BOTH, padx=8, pady=8)
        self.selectedPathLabel.pack(side=tk.LEFT, padx=(8, 0))
        self.browse_button.pack(side=tk.RIGHT, padx=(0, 8), pady=4)

    def browseFolder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selectedPath.set(folder_path)

        self.callback(self.selectedPath.get())
