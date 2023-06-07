from tkinter import Tk
import tkinter as tk
from utils.settings import Settings

from widgets.folder_select_widget import FolderSelector
from widgets.object_select_widget import ObjectSelector
from widgets.proceed_button_widget import ProceedButton

from views.dates_select import DatesSelectWindow

class ObjectSelectWindow(Tk):
    def __init__(self):
        super().__init__()

        # Window can spawn at the center of parent window
        self.eval('tk::PlaceWindow . center')

        self.title("AstroGenie - Select object")
        self.geometry("600x400")
        self.iconbitmap("assets/icon.ico") # type: ignore
        self.resizable(False, False)


        # Define widgets
        self.folderSelectWidget = FolderSelector(self, label="Select astrophotography folder", buttonLabel="Select folder", callback=self.setFolderCallback)
        self.objectList = ObjectSelector(self, self.folderSelectWidget.selectedPath, label="Select object", callback=lambda: self.proceedBtn.config(state=tk.NORMAL))

        # Button group frame (Left, Right buttons)
        self.buttonGroupFrame = tk.Frame(self)
        self.buttonGroupFrame.pack(side=tk.BOTTOM, pady=10)

        # Define buttons
        self.settingsButton = tk.Button(self.buttonGroupFrame, text="Settings", command=self.openSettingsWindow)
        self.proceedBtn = tk.Button(self.buttonGroupFrame, text="Proceed", command=self.proceedBtnClick, state=tk.DISABLED)

        # Pack buttons
        self.settingsButton.pack(side=tk.LEFT, pady=10)
        self.proceedBtn.pack(side=tk.RIGHT, padx=10)

        self.settings = Settings()
        self.settings.loadJson()
        
        # Let's try load the last used folder
        self.tryLoadFolderHistory()

    def openSettingsWindow(self):
        import views.settings as settings
        settings.SettingsWindow()


    def proceedBtnClick(self):
        # Close this window and open the next one
        self.destroy()

        # Open the next window
        DatesSelectWindow(self.folderSelectWidget.selectedPath.get(), self.objectList.selectedObject.get())
        pass

    def tryLoadFolderHistory(self):
        try:
            self.folderSelectWidget.selectedPath.set(self.settings.defaultImageFolder)
            self.objectList.populateObjectList(self.folderSelectWidget.selectedPath.get())
        except FileNotFoundError:
            pass

    def setFolderCallback(self, folderPath:str):
        self.objectList.populateObjectList(folderPath)

        if self.settings.updateDefaultImageFolderOnLoad:
            self.saveFolderHistory()
        pass

    def saveFolderHistory(self):
        self.settings.defaultImageFolder = self.folderSelectWidget.selectedPath.get()
        self.settings.saveJson()
        pass
