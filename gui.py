import tkinter as tk
from tkinter import ttk, StringVar
import config
import thread_data
from PIL import Image, ImageTk
from time import sleep
from datetime import datetime

class LabelEntry(tk.Frame):
    def __init__(self, parent, text : str, textvariable : StringVar = None):
        super().__init__(parent)
        self.txtvar = StringVar() if textvariable is None else textvariable
        self.label = ttk.Label(self, text=text)
        self.label.pack(side='left')
        self.entry = ttk.Entry(self,textvariable=textvariable)
        self.entry.pack(side='left')
    # Get entry value
    def get(self):
        return self.txtvar.get()
    # Set entry value
    def set(self, value):
        self.txtvar.set(value)
    # Set label text
    def set_label(self, value : str):
        self.label.config(text=value)

class LabelCombo(tk.Frame):
    def __init__(self, parent, text : str, values : list, textvariable : StringVar = None):
        super().__init__(parent)
        self.txtvar = StringVar() if textvariable is None else textvariable
        self.label = ttk.Label(self, text=text)
        self.label.pack(side='left')
        self.combobox = ttk.Combobox(self, textvariable=textvariable, values=values)
        self.combobox.pack(side='left')
    # Get combo value
    def get(self):
        return self.combobox.get()
    # Set combo value
    def set(self, value : str):
        self.combobox.set(value)
    # Set available values
    def set_values(self, values):
        self.combobox.config(values=values)

class ModelConfigWindow(tk.Frame):
    def __init__(self, parent, gestures : int):
        super().__init__(parent)
        self.title = ttk.Label(self,text='Config')
        self.title.pack()
        self.names = []
        self.controls = []
        for i in range(gestures):
            le = LabelEntry(self,text=str(i))
            lc = LabelCombo(self,text=str(i), values=config.ACTIONNAMES)
            le.pack()
            lc.pack()
            self.names.append(le)
            self.controls.append(lc)
    def updateDisplay(config : dict):
        pass
    def saveConfig():
        pass

class TrainWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.title = ttk.Label(self,text='Customize')
        self.title.pack()
        ModelConfigWindow(self,3).pack(side='left')
        
        

class OptionsWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.title = ttk.Label(self,text='Options')
        self.title.pack()

class StatusWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.title = ttk.Label(self,text='Status')
        self.title.pack()
        
        self.fps = 60
        self.fps_entry = LabelEntry(self, text='Preview framerate', textvariable=StringVar(value=str(self.fps)))
        self.fps_entry.pack()
        
        self.apply_button = ttk.Button(self, text='apply', command=self.update)
        self.apply_button.pack()

        self.cameraWindow = ttk.Label(self,text='Waiting for camera...')
        self.cameraWindow.pack()
        self.camera_after = None
        self.update_cameraView()
    
    def update_cameraView(self):
        if thread_data.cameraView is not None and self.winfo_viewable() == 1:
            self.cameraImage = ImageTk.PhotoImage(image=thread_data.cameraView)
            self.cameraWindow.configure(text=datetime.now(), image=self.cameraImage)
        self.camera_after = self.after(self.fps, self.update_cameraView)
    
    def update(self):
        var = self.fps_entry.get()
        if var.isdigit(): 
            var = 1000 / int(var)
            self.fps = int(var)
            if self.camera_after is not None:
                self.after_cancel(self.camera_after)
                self.camera_after = self.after(self.fps, self.update_cameraView)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Hand Cursor")
        self.geometry("540x540")
        self.tabs = ttk.Notebook(self)
        self.tabs.add(StatusWindow(self.tabs), text='Status')
        self.tabs.add(TrainWindow(self.tabs), text='Customize')
        self.tabs.add(OptionsWindow(self.tabs), text='Options')
        self.tabs.pack(fill='both')

        self.protocol("WM_DELETE_WINDOW", self.exit)
    
    def spawn_child(self):
        child = TrainWindow(self)
        child.transient(self)
    
    def exit(self):
        thread_data.exit_event.set()
        self.destroy()

window = MainWindow()
def startGUI():
    window.mainloop()  


if __name__ == '__main__':
    startGUI()