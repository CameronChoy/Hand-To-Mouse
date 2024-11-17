import tkinter as tk
from tkinter import ttk
import config
import thread_data
from PIL import Image, ImageTk
from time import sleep
from datetime import datetime

class LabelEntry(tk.Frame):
    def __init__(self, parent, text : str, textvariable : str = None):
        super().__init__(parent)
        ttk.Label(self, text=text).pack(side='left')
        self.entry = ttk.Entry(self,textvariable=textvariable).pack(side='left')
    def get(self):
        return self.entry.get()

class LabelCombo(tk.Frame):
    def __init__(self, parent, text : str, values : list, textvariable : str = None):
        super().__init__(parent)
        ttk.Label(self, text=text).pack(side='left')
        self.combobox = ttk.Combobox(self, textvariable=textvariable, values=values).pack(side='left')
    def get(self):
        return self.combobox.get()

class ModelConfigWindow(tk.Frame):
    def __init__(self, parent, gestures : int):
        super().__init__(parent)
        ttk.Label(self,text='Config').pack()
        self.names = []
        self.controls = []
        for i in range(gestures):
            self.names.append(LabelEntry(self,text=str(i)).pack())
            self.controls.append(LabelCombo(self,text=str(i), values=config.ACTIONNAMES).pack())
    
    def updateDisplay(config : dict):
        pass
    def saveConfig():
        pass

    

class TrainWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self,text='Customize').pack()
        ModelConfigWindow(self,3).pack()
        

class OptionsWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self,text='Options').pack()

class StatusWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self,text='Status').pack()
        self.cameraWindow = ttk.Label(self,text='Loading camera...')
        self.cameraWindow.pack()
        self.update_cameraView()
    
    def update_cameraView(self):
        if thread_data.cameraView is not None and self.winfo_viewable() == 1:
            self.cameraImage = ImageTk.PhotoImage(image=thread_data.cameraView)
            self.cameraWindow.configure(text=datetime.now(), image=self.cameraImage)
        self.after(64, self.update_cameraView)

        

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
    



def startGUI():
    window = MainWindow()
    window.mainloop()  


if __name__ == '__main__':
    startGUI()