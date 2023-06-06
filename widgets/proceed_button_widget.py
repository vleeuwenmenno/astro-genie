import tkinter as tk


class ProceedButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.pack(fill=tk.X, padx=8, pady=8)
        self.config(state=tk.DISABLED)