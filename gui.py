import tkinter as tk
from tkinter import ttk, StringVar, filedialog
from cursor import MouseStatus
import json
import config
from config import ConfigKey, ACTIONNAMES, ActionName
import thread_data
from PIL import Image, ImageTk
from time import sleep
from datetime import datetime

class LabelEntry(tk.Frame):
    def __init__(self, parent, text : str = "", textvariable : StringVar = None, initval : str = ""):
        super().__init__(parent)
        self.txtvar = StringVar() if textvariable is None else textvariable
        self.label = ttk.Label(self, text=text)
        self.label.pack(side='left')
        self.entry = ttk.Entry(self,textvariable=self.txtvar)
        self.entry.pack(side='left')
        self.txtvar.set(initval)
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
    def __init__(self, parent, text : str = "", values : list = [], textvariable : StringVar = None, initval : str = ""):
        super().__init__(parent)
        self.txtvar = StringVar() if textvariable is None else textvariable
        self.label = ttk.Label(self, text=text)
        self.label.pack(side='left')
        self.combobox = ttk.Combobox(self, textvariable=textvariable, values=values)
        self.combobox.pack(side='left')
        self.combobox.set(initval)
    # Get combo value
    def get(self):
        return self.combobox.get()
    # Set combo value
    def set(self, value : str):
        self.combobox.set(value)
    # Set available values
    def set_values(self, values):
        self.combobox.config(values=values)
    # Set label text
    def set_label(self, value : str):
        self.label.config(text=value)

class LabelCheck(tk.Frame):
    def __init__(self, parent, text : str = "", labelside = 'top', initval : bool = False, command = None):
        super().__init__(parent)
        self.checkval = tk.BooleanVar(value = initval)
        self.label = ttk.Label(self, text=text)
        self.label.pack(side=labelside)
        self.check = ttk.Checkbutton(self, variable=self.checkval, command=command)
        self.check.pack()
    # Get checkbox value
    def get(self):
        return self.checkval.get()
    # Set checkbox value
    def set(self, value : bool):
        self.checkval.set(value)
    # Set label text
    def set_label(self, value : str):
        self.label.config(text=value)

class ModelConfigWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.title = ttk.Label(self,text='Config')
        self.title.pack()
        self.names = []
        self.controls = []
        self.flagChecks = {}
        self.flagframe = tk.Frame(self)
        self.flagframe.pack()
        self.currentselect = -1
        for flag in vars(MouseStatus):
            if flag.startswith('_'): continue
            checkButton = LabelCheck(self.flagframe, text=flag.lower(), command=self.setSelectedToCustom)
            checkButton.pack(anchor='nw', side='left', padx=4)
            self.flagChecks[flag] = checkButton
        
        if config.model_config != None: 
            self.updateDisplay(config.model_config)
    
    # Update configs being displayed
    def updateDisplay(self, config : dict):
        for x in self.names:
            x.destroy()
        for x in self.controls:
            x.destroy()

        self.names = []
        self.controls = []
        gc = config[ConfigKey.GESTURECOUNT]
        for i in range(gc):
            le = LabelEntry(self,text=f"Name {i}", initval=config[ConfigKey.GESTURES][str(i)])
            c = config[ConfigKey.CONTROLS][str(i)]
            initval = ActionName[c] if c in ActionName else str(c)
            lc = LabelCombo(self,text=f"Action {i}", values=ACTIONNAMES, initval=initval)

            selectfunc = lambda event, id=i: self.updateFlags(id)
            le.bind("<FocusIn>", selectfunc)
            lc.bind("<FocusIn>", selectfunc)
            
            le.pack(anchor='nw')
            lc.pack(anchor='nw', pady=(4,10))
            self.names.append(le)
            self.controls.append(lc)
    
    # Update flag checkboxes to selected gesture
    def updateFlags(self, id):

        # Signify what's selected
        if self.currentselect != -1:
            self.names[self.currentselect].configure(bg="SystemButtonFace")
            self.controls[self.currentselect].configure(bg="SystemButtonFace")
        self.currentselect = id
        self.names[self.currentselect].configure(bg="#FF0000")
        self.controls[self.currentselect].configure(bg="#FF0000")

        controls = self.convertStrToFlags(self.controls[id].get())
        for flag in vars(MouseStatus):
            if flag.startswith('_'): continue
            f = getattr(MouseStatus, flag)
            self.flagChecks[flag].set(controls & f != 0)

    # Update currently selected gesture action to flag checkboxes
    def setSelectedToCustom(self):
        if self.currentselect == -1: return
        self.controls[self.currentselect].set(self.convertFlagsToStr())

    # Convert string to flag
    def convertStrToFlags(self, controls):

        # Binary string
        try:
            flags = int(controls,2)
            return flags
        except ValueError:
            pass

        flags = 0
        match controls:
            case "Left click":
                flags = MouseStatus.LMOUSE_DOWN
            case "Right click":
                flags = MouseStatus.RMOUSE_DOWN
            case "Middle click":
                flags = MouseStatus.MIDDLE_DOWN
            case "Scroll up":
                flags = MouseStatus.WHEEL
            case "Scroll down":
                flags = MouseStatus.WHEEL
            case _:
                if controls.isdigit():
                    flags = int(controls)

        return flags
    
    # Convert flag checkboxes to an string digit
    def convertFlagsToStr(self):
        flags = 0
        for flag in vars(MouseStatus):
            if flag.startswith('_') or not self.flagChecks[flag].get(): continue
            f = getattr(MouseStatus, flag)
            flags |= f
        return str(flags)
    
    # Apply config options
    def applyConfig(self):
        gc = len(self.names)
        config_data = {ConfigKey.GESTURES : {}, ConfigKey.CONTROLS : {}, ConfigKey.GESTURECOUNT : gc}
        for i in range(gc):
            name = self.names[i].get()
            config_data[ConfigKey.GESTURES][str(i)] = name

            controls = self.convertStrToFlags(self.controls[i].get())
            config_data[ConfigKey.CONTROLS][str(i)] = controls
        return config_data

    # Save and apply config options
    def saveConfig(self, path : str):
        config_data = self.applyConfig()
        try:
            with open(f"{path}/config.json","w") as f:
                json.dump(config_data,f)
        except OSError as e:
            print(e)
        

    # Reset flag checkboxes
    def clearFlags(self):
        self.currentselect = -1
        for flag in vars(MouseStatus):
            if flag.startswith('_'): continue
            self.flagChecks[flag].set(False)


class TrainWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.title = ttk.Label(self,text='Customize')
        self.title.pack()
        self.currentdir = ""

        self.modelFolderFrame = ttk.Frame(self)
        self.modelFolderFrame.pack(side='top', anchor='nw', fill='none')
        self.modelFolderLabel = ttk.Label(self.modelFolderFrame, text="--No model selected--")
        self.modelFolderLabel.pack(side='left')
        self.modelFolderDialog = ttk.Button(self.modelFolderFrame, text="Select Model dir", command=self.selectModelFolderPath)
        self.modelFolderDialog.pack(side='left')

        self.configWindow = ModelConfigWindow(self)
        self.configWindow.pack(side='top', anchor='nw',fill='none')

        self.applyConfigButton = ttk.Button(self, text="Apply", command=self.configWindow.applyConfig)
        self.saveConfigButton = ttk.Button(self, text="Save and Apply", command=lambda path = self.currentdir: self.configWindow.saveConfig(path=path))
        self.saveConfigButton.pack(side='right', anchor='ne')
        self.applyConfigButton.pack(side='right', anchor='ne')
    
    # Select model directory
    def selectModelFolderPath(self):
        dir = filedialog.askdirectory()
        if dir == '': return
        config_file = config.load_config_file(dir, False)
        if config.valid_config_file(config_file):
            self.configWindow.updateDisplay(config_file)
            self.configWindow.clearFlags()
            self.modelFolderLabel.config(text=dir)
            self.currentdir = dir
        else:
            self.modelFolderLabel.config(text="Failed to find 'config.json'")
        
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

        self.apply_button = ttk.Button(self, text='Apply', command=self.update)
        self.apply_button.pack(side='right',anchor='ne')
        
        self.fps = 60
        self.fps_entry = LabelEntry(self, text='Preview framerate', textvariable=StringVar(value=str(self.fps)))
        self.fps_entry.pack()

        self.cameraWindow = ttk.Label(self,text='Waiting for camera...')
        self.cameraWindow.pack()
        self.camera_after = None
        self.update_cameraView()
    
    # Render latest frame from camera
    def update_cameraView(self):
        if thread_data.cameraView is not None and self.winfo_viewable() == 1:
            self.cameraImage = ImageTk.PhotoImage(image=thread_data.cameraView)
            self.cameraWindow.configure(text=datetime.now(), image=self.cameraImage)
        self.camera_after = self.after(self.fps, self.update_cameraView)
    
    # Apply preview frame option
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
        self.geometry("1280x720")
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

MainApplication = MainWindow()
def startGUI():
    MainApplication.mainloop()  


if __name__ == '__main__':
    startGUI()