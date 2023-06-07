import datetime
import os
import tkinter as tk
from typing import Callable
from utils.settings import Settings

from widgets.select_widget import Selector

class DatesSelector(tk.Tk):
    def __init__(self, window, datesFolder:tk.StringVar, label:str="", callback:Callable=Callable) -> None:
        self.selector = Selector(window, datesFolder, self.populateObjectList, label, callback, multiSelect=True)
        self.selectedDate = self.selector.selectedItems

    def populateObjectList(self, folderPath: str):
        settings = Settings()
        settings.loadJson()

        dateFormat = settings.dateFormat

        # Return only YYYY-MM-DD folders with validated date format
        return [
            folder for folder in os.listdir(folderPath)
            if os.path.isdir(os.path.join(folderPath, folder)) and self.validateDate(folder, dateFormat)
        ]
    
    def validateDate(self, date:str, dateFormat:str) -> bool:
        try:
            datetime.datetime.strptime(date, dateFormat)
            return True
        except ValueError:
            return False