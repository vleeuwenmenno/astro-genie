import tkinter as tk


class StatusBar(tk.Frame):
    def __init__(self, window, selectedItem, path, textLeft:tk.StringVar, textRight:tk.StringVar) -> None:

        # Create the labels for the status bar
        self = tk.Frame(window, bd=1, relief=tk.SUNKEN)
        self.pack(side=tk.BOTTOM, fill=tk.X)

        left_status_label = tk.Label(self, textvariable=textLeft, bd=0, anchor=tk.W)
        left_status_label.pack(side=tk.LEFT, fill=tk.X, padx=(5, 0))

        right_status_label = tk.Label(self, textvariable=textRight, bd=0, anchor=tk.E)
        right_status_label.pack(side=tk.RIGHT, fill=tk.X, padx=(0, 5))