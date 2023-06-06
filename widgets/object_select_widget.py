import os
import tkinter as tk
from typing import Callable

from widgets.select_widget import Selector

class ObjectSelector(tk.Tk):
    def __init__(self, window, objectFolder:tk.StringVar, label:str="", callback:Callable=Callable) -> None:
        self.catalogWhitelist = ["M ", "NGC ", "IC "]
        self.selector = Selector(window, objectFolder, self.populateObjectList, label, callback)
        self.selectedObject = self.selector.selectedItems

    def populateObjectList(self, folderPath: str):
        return [
            name for name in os.listdir(folderPath) if any(
                catalog in name for catalog in self.catalogWhitelist
            )
        ]