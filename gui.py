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
    def get(self):
        return self.txtvar.get()

class LabelCombo(tk.Frame):
    def __init__(self, parent, text : str, values : list, textvariable : StringVar = None):
        super().__init__(parent)
        self.txtvar = StringVar() if textvariable is None else textvariable
        ttk.Label(self, text=text).pack(side='left')
        self.combobox = ttk.Combobox(self, textvariable=textvariable, values=values)
        self.combobox.pack(side='left')
    def get(self):
        return self.txtvar.get()

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
        ModelConfigWindow(self,3).pack()
        

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
        self.cameraWindow = ttk.Label(self,text='Loading camera...')
        self.cameraWindow.pack()

        self.fps = 64
        self.fps_entry = LabelEntry(self, text='Preview fps', textvariable=StringVar(value=str(self.fps)))
        self.fps_entry.pack()
        
        self.apply_button = ttk.Button(self, text='apply', command=self.update)
        self.apply_button.pack()
        self.update_cameraView()
    
    def update_cameraView(self):
        if thread_data.cameraView is not None and self.winfo_viewable() == 1:
            self.cameraImage = ImageTk.PhotoImage(image=thread_data.cameraView)
            self.cameraWindow.configure(text=datetime.now(), image=self.cameraImage)
        self.after(self.fps, self.update_cameraView)
    
    def update(self):
        var = self.fps_entry.get()
        if var.isdigit(): 
            self.fps = int(var)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Hand Cursor")
        self.geometry("300x300")
        self.tabs = ttk.Notebook(self)
        self.tabs.add(StatusWindow(self.tabs), text='Status')
        self.tabs.add(TrainWindow(self.tabs), text='Customize')
        self.tabs.add(OptionsWindow(self.tabs), text='Options')
        self.tabs.pack(fill='both')

        self.protocol("WM_DELETE_WINDOW", self.exit)
        #self.frm = ttk.Frame(self, padding=10)
        #self.frm.grid()
        #ttk.Label(self.frm, text='Uhhh').grid(column=0,row=0)
        #ttk.Button(self.tabs,text="Exit",command=self.exit).pack()
        #ttk.Button(self.frm,text="child",command=self.spawn_child).grid(column=2,row=0)
    
    def spawn_child(self):
        child = TrainWindow(self)
        child.transient(self)
    
    def exit(self):
        thread_data.exit_event.set()
        print('exiting')
        self.destroy()

window = MainWindow()
def startGUI():
    window.mainloop()  


if __name__ == '__main__':
    startGUI()