import os
import tkinter as tk
from typing import Callable

from widgets.select_widget import Selector

class DatesSelector(tk.Tk):
    def __init__(self, window, datesFolder:tk.StringVar, label:str="", callback:Callable=Callable) -> None:
        self.selector = Selector(window, datesFolder, self.populateObjectList, label, callback, multiSelect=True)
        self.selectedDate = self.selector.selectedItems

    def populateObjectList(self, folderPath: str):
        # Return only YYYY-MM-DD folders with validated date format
        return [
            name for name in os.listdir(folderPath) if len(name) == 10 and name[4] == "-" and name[7] == "-"
        ]