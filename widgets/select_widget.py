import json
import os
import tkinter as tk
from typing import Callable

class Selector(tk.Tk):
    def __init__(self, window, objectFolder:tk.StringVar, getListData:Callable, label:str="", callback:Callable=Callable, multiSelect:bool=False) -> None:
        self.selectedItems = tk.StringVar()
        self.frame = tk.LabelFrame(window, text=label)
        self.list = tk.Listbox(self.frame)
        self.scrollbar = tk.Scrollbar(self.list, orient=tk.VERTICAL)
        self.objectFolderPath = objectFolder
        self.callback = callback

        self.frame.pack(fill=tk.BOTH, padx=8, pady=8, expand=1)
        self.list.pack(fill=tk.BOTH, padx=8, pady=8, expand=1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.config(command=self.list.yview)

        # Set list to multi-select if needed
        if multiSelect:
            self.list.config(selectmode=tk.MULTIPLE)

        # When object folder path changes, update list
        objectFolder.trace("w", lambda *args: self.listUpdate(getListData(objectFolder.get())))

        # Bind to list selection change event to update selected path
        self.list.bind("<<ListboxSelect>>", self.listboxSelect)
        
        # Populate list
        if objectFolder.get() != "" and os.path.isdir(objectFolder.get()):
            self.listUpdate(getListData(objectFolder.get()))

    def listUpdate(self, data:list):
        self.list.delete(0, tk.END)
        for name in data:
            self.list.insert(tk.END, name)
        pass

    def listboxSelect(self, event):
        # Get selected item(s) value(s)
        if self.list.curselection():
            if len(self.list.curselection()) == 1 and not self.list["selectmode"] == tk.MULTIPLE:
                self.selectedItems.set(self.list.get(self.list.curselection()))
            else:
                self.selectedItems.set(json.dumps([self.list.get(i) for i in self.list.curselection()]))

        if self.callback:
            if len(self.callback.__code__.co_varnames) >= 2 and self.callback.__code__.co_varnames[1] == "selectedItems":
                self.callback(json.loads(self.selectedItems.get()))
            else:
                self.callback()
        pass