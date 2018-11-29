import numpy as np
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import tkinter.font as tkFont
from PIL import ImageTk, Image
from Solver import Simulator
import os
import errno



DEFAULT_IMAGE = "Image_Assets/default.png"
PLAY_BUTTON_IMAGE = "Image_Assets/PlayButtonB.png"
PAUSE_BUTTON_IMAGE = "Image_Assets/PauseButtonB.png"
BACK_BUTTON_IMAGE = "Image_Assets/BackButtonB.png"
FORWARD_BUTTON_IMAGE = "Image_Assets/ForwardButtonB.png"

DEFAULT_OPEN_DIR = "Output\\"
DEFAULT_OUT_DIR = "Output\\"

DEFAULT_DATA_SAVE_DIR = "Output\\Simulation_Data\\"
DEFAULT_COMP_SAVE_DIR = "Output\\Component_Plots\\"
DEFAULT_PARAM_SAVE_DIR = "Output\\Parametric_Plots\\"
DEFAULT_ANIM_SAVE_DIR = "Output\\Animations\\"

DEFAULT_SAVE_DIRS = {
    "data":DEFAULT_DATA_SAVE_DIR,
    "compPlot":DEFAULT_COMP_SAVE_DIR,
    "paramPlot":DEFAULT_PARAM_SAVE_DIR,
    "anim":DEFAULT_ANIM_SAVE_DIR
}

DEFAULT_SIM_DELTA_TIME = 0.25


def grabTruePath(fileInDirectory):
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
    realPath = os.path.join(__location__, fileInDirectory)

    return realPath

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.FRAME_DELAY = 1/60 * 1000

        self.isAnimLoaded = False
        self.animFrameNumber = -1
        self.allAnimFrames = []
        self.isPlaying = False
        self.currentFrame = 0

        self.plusMinus = tk.IntVar(value=1)
        self.inputMode = tk.IntVar(value=0)
        self.displayMode = tk.IntVar(value=-1)


        self.s1 = tk.IntVar(value=0)
        self.s2 = tk.IntVar(value=0)
        self.s3 = tk.IntVar(value=0)
        self.s4 = tk.IntVar(value=0)


        self.fileNameToSave = tk.StringVar(value="Valid Filename")
        self.fileNameToSave.trace("w", lambda *_, var=self.fileNameToSave: self.validateName(var, "fileName"))

        self.timeStepVal = tk.StringVar(value="Positive Integer")
        self.timeStepVal.trace("w", lambda *_, var=self.timeStepVal: self.validateTimeSteps(var, "timeStep"))

        self.eVal = tk.StringVar(value="Positive Float")
        self.eVal.trace("w", lambda *_, var=self.eVal: self.validatePosFloat(var, "eVal"))

        self.lVal = tk.StringVar(value="Float")
        self.lVal.trace("w", lambda *_, var=self.lVal: self.validateFloat(var, "lVal"))

        self.rValA = tk.StringVar(value="Positive Float")
        self.rValA.trace("w", lambda *_, var=self.rValA: self.validatePosFloat(var, "rValA"))

        self.pValA = tk.StringVar(value="Float")
        self.pValA.trace("w", lambda *_, var=self.pValA: self.validateFloat(var, "pValA"))

        self.urVal = tk.StringVar(value="Float")
        self.urVal.trace("w", lambda *_, var=self.urVal: self.validateFloat(var, "urVal"))

        self.upVal = tk.StringVar(value="Float")
        self.upVal.trace("w", lambda *_, var=self.upVal: self.validateFloat(var, "upVal"))

        self.rValB = tk.StringVar(value="Positive Float")
        self.rValB.trace("w", lambda *_, var=self.rValB: self.validatePosFloat(var, "rValB"))

        self.pValB = tk.StringVar(value="Float")
        self.pValB.trace("w", lambda *_, var=self.pValB: self.validateFloat(var, "pValB"))

        self.validity = {
            "fileName":False,
            "timeStep":False,
            "eVal":False,
            "lVal":False,
            "rValA":False,
            "pValA":False,
            "urVal":False,
            "upVal":False,
            "rValB":False,
            "pValB":False
        }

        self.enterStructures = {}

        self.workDone = tk.IntVar(value=0)

        realPath = grabTruePath(DEFAULT_OUT_DIR)

        if not os.path.isdir(realPath):
            try:
                os.mkdir(realPath)
            except OSError as e:
                raise

        for directory in DEFAULT_SAVE_DIRS.values():
            realPath = grabTruePath(directory)
            if not os.path.isdir(realPath):
                try:
                    os.mkdir(realPath)
                except OSError as e:
                    raise

        self.master = master
        self.pack()
        self.configStyles()
        self.createWidgets()

    def configStyles(self):
        style = ttk.Style()
        style.configure("T.TButton", foreground="black", background="grey")
        style.configure("I.TButton", foreground="white", background="white")
        style.configure("BW.TLabel", foreground="white", background="black")

        style.configure("Title.TLabel", font=tkFont.Font(family="Times New Roman", size=18))

        style.configure("Invalid.TEntry", foreground="#ff7153")
        style.configure("Empty.TEntry", foreground="grey")
        style.configure("Valid.TEntry", foreground="#278e00")

        style.configure("Invalid.TCheckbutton", foreground="#ff7153")
        style.configure("Empty.TCheckbutton", foreground="grey")
        style.configure("Valid.TCheckbutton", foreground="#278e00")

        style.configure("Invalid.TRadiobutton", foreground="#ff7153")
        style.configure("Empty.TRadiobutton", foreground="grey")
        style.configure("Valid.TRadiobutton", foreground="#278e00")

        return

    def createWidgets(self):
        path = grabTruePath(DEFAULT_IMAGE)
        defImg = ImageTk.PhotoImage(Image.open(path))

        self.columnconfigure(2)

        pVal = 4

        self.plotLabel = ttk.Label(self, text="Currently Displaying: None", style="Title.TLabel")
        self.plotLabel.grid(row=0, column=0, columnspan=7, padx=16)

        self.imagePanel = ttk.Label(self, image=defImg, style="BW.TLabel")
        self.imagePanel.image = defImg
        self.imagePanel.grid(row=1, column=0, columnspan=7, padx=16)

        self.gifScale = tk.Scale(self, from_=0, to=200, orient=tk.HORIZONTAL, length=300)
        self.gifScale["command"] = self.changeFrame
        self.gifScale.grid(row=3, column=0, columnspan=7)
        self.gifScale.configure(state="disabled", bg='grey', fg='grey')

        self.containerFrame = tk.Frame(self)

        path = grabTruePath(BACK_BUTTON_IMAGE)
        bImg = ImageTk.PhotoImage(Image.open(path))
        self.backButton = ttk.Button(self.containerFrame, image=bImg, style="I.TButton")
        self.backButton.image = bImg
        self.backButton["command"] = self.animRestart
        self.backButton.pack(side="left", fill=None, expand=False)
        self.backButton.state(["disabled"])

        path = grabTruePath(PLAY_BUTTON_IMAGE)
        playImg = ImageTk.PhotoImage(Image.open(path))
        path = grabTruePath(PAUSE_BUTTON_IMAGE)
        pauseImg = ImageTk.PhotoImage(Image.open(path))
        self.playButton = ttk.Button(self.containerFrame, image=playImg, style="I.TButton")
        self.playButton.image = (playImg, pauseImg)
        self.playButton["command"] = self.flipAnimPlayState
        self.playButton.pack(side="left", fill=None, expand=False)
        self.playButton.state(["disabled"])

        path = grabTruePath(FORWARD_BUTTON_IMAGE)
        fImg = ImageTk.PhotoImage(Image.open(path))
        self.forwardButton = ttk.Button(self.containerFrame, image=fImg, style="I.TButton")
        self.forwardButton.image = fImg
        self.forwardButton["command"] = self.animSkipToEnd
        self.forwardButton.pack(side="left", fill=None, expand=False)
        self.forwardButton.state(["disabled"])

        self.containerFrame.grid(row=4, column=0, columnspan=7)

        self.loadButton = ttk.Button(self, style="T.TButton")
        self.loadButton["text"] = "Load"
        self.loadButton["command"] = self.loadFileFromDialog
        self.loadButton.grid(row=5, column=0, sticky="W")

        self.simulateButton = ttk.Button(self, style="T.TButton")
        self.simulateButton["text"] = "Simulate"
        self.simulateButton["command"] = self.displayRunConfigurer
        self.simulateButton.grid(row=5, column=6, sticky="E")

        return

    #Sends an animation back to the beginning of its run time
    def animRestart(self):
        self.currentFrame = 0
        self.gifScale.set(self.currentFrame)
        self.setLabelFrame(0, self.allAnimFrames, self.animFrameNumber)
        return

    #Pauses or plays animation from last pause point depending on previous state
    #Also changes button appearance back and forth
    def flipAnimPlayState(self):
        self.isPlaying = not self.isPlaying
        if self.isPlaying:
            self.playButton["image"] = self.playButton.image[1]
        else:
            self.playButton["image"] = self.playButton.image[0]
        return

    #Skips to last frame of animation
    def animSkipToEnd(self):
        finalFrameNum = self.animFrameNumber - 1
        self.currentFrame = finalFrameNum
        self.gifScale.set(self.currentFrame)
        self.setLabelFrame(finalFrameNum, self.allAnimFrames, self.animFrameNumber)
        return


    def getAnimFrameLength(self, animFilePath):
        im = Image.open(animFilePath)
        frameNum = 0
        while True:
            try:
                im.seek(frameNum)
            except EOFError:
                break
            frameNum += 1
        return frameNum

    def reconstructGif(self, animFilePath, frameNumber):
        baseFrame = Image.open(animFilePath)
        baseFrame.seek(0)
        firstFrame = baseFrame
        allFrames = [firstFrame]

        lastFrame = firstFrame
        sizeX, sizeY = lastFrame.size
        frameBox = (0, 0, sizeX, sizeY)

        for index in range(1,frameNumber):
            baseFrame.seek(index)

            newFrame = lastFrame.copy()
            newFrame.paste(baseFrame, box=frameBox)

            allFrames.append(newFrame)
            lastFrame = newFrame

        return allFrames[1:]

    def setLabelFrame(self, frame, allAnimFrames, animFrameNumber):
        if frame < animFrameNumber:
            im = ImageTk.PhotoImage(allAnimFrames[frame])
            self.imagePanel["image"] = im
            self.imagePanel.image = im
        return


    def loadFileFromPath(self, filePath):
        if filePath == '':
            return False
        else:
            self.currentFrame = 0

            if  '.gif' in filePath:
                self.isAnimLoaded = True


                self.backButton.state(["!disabled"])
                self.playButton.state(["!disabled"])
                self.forwardButton.state(["!disabled"])

                baseFrameNumber = self.getAnimFrameLength(filePath)

                self.allAnimFrames = self.reconstructGif(filePath, baseFrameNumber)
                self.animFrameNumber = baseFrameNumber - 1


                self.gifScale.config(state="active", fg='white', bg='grey40',
                    to=self.animFrameNumber)
                self.setLabelFrame(0, self.allAnimFrames, self.animFrameNumber)


            else:
                if '.png' in filePath:
                    self.isAnimLoaded = False

                    self.backButton.state(["disabled"])
                    self.playButton.state(["disabled"])
                    self.forwardButton.state(["disabled"])

                    self.gifScale.set(1)
                    self.gifScale.config(state="disabled", fg='grey', bg='grey')


                    self.animFrameNumber = -1

                    img = ImageTk.PhotoImage(Image.open(filePath))
                    self.imagePanel["image"] = img
                    self.imagePanel.image = img

        if '/' in filePath:
            self.plotLabel["text"] = "Currently Displaying: " + filePath.split("/")[-1]
        if '\\' in filePath:
            self.plotLabel["text"] = "Currently Displaying: " + filePath.split("\\")[-1]

        return True

    #Creates a pop-up window that asks the user to select the file to be loaded
    def loadFileFromDialog(self):
        baseDirectory = grabTruePath(DEFAULT_OPEN_DIR)
        filePathToLoad = tk.filedialog.askopenfilename(
            title="Load File",
            filetypes = [
                ("PNG File", "*.png"),
                ("GIF File", "*.gif")
                ],
            initialdir=baseDirectory
            )
        success = self.loadFileFromPath(filePathToLoad)
        return success

    def validateName(self, inputStringVar, key):
        isValid = True
        inputString = inputStringVar.get()
        if inputString == '':
            isValid = False
        forbidden = '/\\?%*:|\"<>. '
        for char in forbidden:
            isValid = isValid and not char in inputString
            if not isValid:
                break
        self.validity[key] = isValid
        self.checkOverallValidity()
        return isValid

    def validateTimeSteps(self, inputStringVar, key):
        isValid = True

        inputString = inputStringVar.get()
        try:
            value = int(inputString)
            fValue = float(inputString)
        except ValueError:
            value = 0
            fValue = 0
            isValid = False
        if float(value) != fValue:
            isValid = False
        if value <= 0:
            isValid = False
        self.validity[key] = isValid
        self.checkOverallValidity()
        return isValid

    def validatePosFloat(self, inputStringVar, key):
        isValid = True
        inputString = inputStringVar.get()
        try:
            value = float(inputString)
        except ValueError:
            value = 0
            isValid = False
        if value <= 0:
            isValid = False
        self.validity[key] = isValid
        self.checkOverallValidity()
        return True

    def validateFloat(self, inputStringVar, key):
        isValid = True
        inputString = inputStringVar.get()
        try:
            value = float(inputString)
        except ValueError:
            value = 0
            isValid = False
        self.validity[key] = isValid
        self.checkOverallValidity()
        return True

        #Deactivates the B radio button's input and reactivates the A button's one
    def flipA(self):
        self.lEnterA.state(["!disabled"])
        self.eEnterA.state(["!disabled"])
        self.rEnterA.state(["!disabled"])
        self.pEnterA.state(["!disabled"])

        self.urEnterB.state(["disabled"])
        self.upEnterB.state(["disabled"])
        self.rEnterB.state(["disabled"])
        self.pEnterB.state(["disabled"])

        self.checkOverallValidity()

        return

    #Deactivates the A radio button's input and reactivates the B button's one
    def flipB(self):
        self.urEnterB.state(["!disabled"])
        self.upEnterB.state(["!disabled"])
        self.rEnterB.state(["!disabled"])
        self.pEnterB.state(["!disabled"])

        self.lEnterA.state(["disabled"])
        self.eEnterA.state(["disabled"])
        self.rEnterA.state(["disabled"])
        self.pEnterA.state(["disabled"])

        self.checkOverallValidity()

        return

    def assessDisplayMode(self):
        self.checkOverallValidity()
        return

    def checkOverallValidity(self):
        areInputsValid = True
        keysCase1 = ["fileName", "timeStep", "eVal", "lVal", "rValA", "pValA"]
        keysCase2 = ["fileName", "timeStep", "urVal", "upVal", "rValB", "pValB"]

        if self.inputMode.get() == 0:
            for key in keysCase1:
                if self.validity[key]:
                    self.enterStructures[key].config(style="Valid.TEntry")
                if not self.validity[key]:
                    self.enterStructures[key].config(style="Invalid.TEntry")
                areInputsValid = areInputsValid and self.validity[key]

            for keyIndex in range(len(keysCase2)):
                key1 = keysCase1[keyIndex]
                key2 = keysCase2[keyIndex]
                if key2 != key1:
                    self.enterStructures[key2].config(style="Empty.TEntry")
        else:
            for key in keysCase2:
                if self.validity[key]:
                    self.enterStructures[key].config(style="Valid.TEntry")
                if not self.validity[key]:
                    self.enterStructures[key].config(style="Invalid.TEntry")
                areInputsValid = areInputsValid and self.validity[key]

            for keyIndex in range(len(keysCase1)):
                key1 = keysCase1[keyIndex]
                key2 = keysCase2[keyIndex]
                if key1 != key2:
                    self.enterStructures[key1].config(style="Empty.TEntry")


        if self.s2.get() == 0:
            self.dispSel1.state(["disabled"])
            if self.displayMode.get() == 0:
                self.displayMode.set(-1)
        if self.s2.get() == 1:
            self.dispSel1.state(["!disabled"])

        if self.s3.get() == 0:
            self.dispSel2.state(["disabled"])
            if self.displayMode.get() == 1:
                self.displayMode.set(-1)
        if self.s3.get() == 1:
            self.dispSel2.state(["!disabled"])

        if self.s4.get() == 0:
            self.dispSel3.state(["disabled"])
            if self.displayMode.get() == 2:
                self.displayMode.set(-1)
        if self.s4.get() == 1:
            self.dispSel3.state(["!disabled"])

        outputsSelected = self.s1.get() + self.s2.get() + self.s3.get() + self.s4.get()

        if outputsSelected == 0:
            self.outSel1.config(style="Invalid.TCheckbutton")
            self.outSel2.config(style="Invalid.TCheckbutton")
            self.outSel3.config(style="Invalid.TCheckbutton")
            self.outSel4.config(style="Invalid.TCheckbutton")
        else:
            self.outSel1.config(style="Valid.TCheckbutton")
            self.outSel2.config(style="Valid.TCheckbutton")
            self.outSel3.config(style="Valid.TCheckbutton")
            self.outSel4.config(style="Valid.TCheckbutton")

        if self.displayMode.get() == -1:
            self.dispSel1.config(style="Invalid.TRadiobutton")
            self.dispSel2.config(style="Invalid.TRadiobutton")
            self.dispSel3.config(style="Invalid.TRadiobutton")
        else:
            self.dispSel1.config(style="Valid.TRadiobutton")
            self.dispSel2.config(style="Valid.TRadiobutton")
            self.dispSel3.config(style="Valid.TRadiobutton")

        #print(areInputsValid)
        #print(outputsSelected)
        #print(self.inputMode.get())

        if outputsSelected != 0 and self.displayMode.get() != -1 and areInputsValid:
            self.goButton.state(["!disabled"])
        else:
            self.goButton.state(["disabled"])

        return



    #Displays pop-up window that lets the user configure the run
    def displayRunConfigurer(self):
        self.rConfig = tk.Toplevel(takefocus=True)
        self.rConfig.title("Configure Run")
        self.rConfig.grab_set()

        pVal = 2

        self.instruct = ttk.Label(self.rConfig, text="Enter Run Parameters", style="Title.TLabel")
        self.instruct.grid(row=0, column=0, columnspan=6, padx=pVal, pady=pVal)

        self.titleInputLabel = ttk.Label(self.rConfig, text="Run Name:")
        self.titleInputLabel.grid(row=1, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)
        self.titleInput = ttk.Entry(self.rConfig, textvariable=self.fileNameToSave)
        self.titleInput.grid(row=2, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)


        self.timeStepInputLabel = ttk.Label(self.rConfig, text="# of Timesteps:")
        self.timeStepInputLabel.grid(row=1, column=4, columnspan=2, sticky='W', padx=pVal, pady=pVal)
        self.timeStepInput = ttk.Entry(self.rConfig, textvariable=self.timeStepVal)
        self.timeStepInput.grid(row=2, column=4, columnspan=4, sticky='W', padx=pVal, pady=pVal)

        self.inputRad1 = ttk.Radiobutton(
            self.rConfig,
            text="Initial Conditions [" + "e, " + u'\u2113' + ",  r, " + u'\u03D5' + "]",
            variable=self.inputMode,
            value=0
            )
        self.inputRad1["command"] = self.flipA
        self.inputRad1.grid(row=3, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)

        self.eEnterLabelA = ttk.Label(self.rConfig, text='e')
        self.eEnterLabelA.grid(row=4, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)
        self.eEnterA = ttk.Entry(self.rConfig, textvariable=self.eVal)
        self.eEnterA.grid(row=4, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.lEnterLabelA = ttk.Label(self.rConfig, text=u'\u2113')
        self.lEnterLabelA.grid(row=5, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)
        self.lEnterA = ttk.Entry(self.rConfig, textvariable=self.lVal)
        self.lEnterA.grid(row=5, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.rEnterLabelA = ttk.Label(self.rConfig, text="r (M)")
        self.rEnterLabelA.grid(row=6, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)
        self.rEnterA = ttk.Entry(self.rConfig, textvariable=self.rValA)
        self.rEnterA.grid(row=6, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.pEnterLabelA = ttk.Label(self.rConfig, text=u'\u03D5' + " (rad)")
        self.pEnterLabelA.grid(row=7, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)
        self.pEnterA = ttk.Entry(self.rConfig, textvariable=self.pValA)
        self.pEnterA.grid(row=7, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.signValidationLabel = ttk.Label(self.rConfig, text="Sign of u" + u'\u1D63')
        self.signValidationLabel.grid(row=8, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)

        self.signSel1 = ttk.Radiobutton(self.rConfig, variable=self.plusMinus, text="+", value=1)
        self.signSel1.grid(row=9, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.signSel2 = ttk.Radiobutton(self.rConfig, variable=self.plusMinus, text="-", value=-1)
        self.signSel2.grid(row=9, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.inputRad2 = ttk.Radiobutton(
            self.rConfig,
            text="Initial Conditions [u" + u'\u1D63' + ", u" + u'\u209A' + ", r, " + u'\u03D5' + "]",
            variable=self.inputMode,
            value=1)

        self.inputRad2["command"] = self.flipB
        self.inputRad2.grid(row=3, column=4, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.urEnterLabelB = ttk.Label(self.rConfig, text="u" + u'\u1D63')
        self.urEnterLabelB.grid(row=4, column=4, sticky='W', padx=pVal, pady=pVal)
        self.urEnterB = ttk.Entry(self.rConfig, textvariable=self.urVal, validate='all', validatecommand=(self.validateFloat, "%P"))
        self.urEnterB.grid(row=4, column=5, sticky='W', padx=pVal, pady=pVal)

        self.upEnterLabelB = ttk.Label(self.rConfig, text="u" + u'\u209A')
        self.upEnterLabelB.grid(row=5, column=4, sticky='W', padx=pVal, pady=pVal)
        self.upEnterB = ttk.Entry(self.rConfig, textvariable=self.upVal, validate='all', validatecommand=(self.validateFloat, "%P"))
        self.upEnterB.grid(row=5, column=5, sticky='W', padx=pVal, pady=pVal)

        self.rEnterLabelB = ttk.Label(self.rConfig, text="r (M)")
        self.rEnterLabelB.grid(row=6, column=4, sticky='W', padx=pVal, pady=pVal)
        self.rEnterB = ttk.Entry(self.rConfig, textvariable=self.rValB, validate='all', validatecommand=(self.validatePosFloat, "%P"))
        self.rEnterB.grid(row=6, column=5, sticky='W', padx=pVal, pady=pVal)

        self.pEnterLabelB = ttk.Label(self.rConfig, text=u'\u03D5' + " (rad)")
        self.pEnterLabelB.grid(row=7, column=4, sticky='W', padx=pVal, pady=pVal)
        self.pEnterB = ttk.Entry(self.rConfig, textvariable=self.pValB, validate='all', validatecommand=(self.validateFloat, "%P"))
        self.pEnterB.grid(row=7, column=5, sticky='W', padx=pVal, pady=pVal)


        self.outSelLabel = ttk.Label(self.rConfig, text="Should Save:")
        self.outSelLabel.grid(row=10, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)

        self.outSel1 = ttk.Checkbutton(self.rConfig, variable=self.s1, text="Data File")
        self.outSel1["command"]= self.checkOverallValidity
        self.outSel1.grid(row=11, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)

        self.outSel2 = ttk.Checkbutton(self.rConfig, variable=self.s2, text="Component Graphs")
        self.outSel2["command"]= self.checkOverallValidity
        self.outSel2.grid(row=12, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)

        self.outSel3 = ttk.Checkbutton(self.rConfig, variable=self.s3, text="Parameterized Graph")
        self.outSel3["command"]= self.checkOverallValidity
        self.outSel3.grid(row=13, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)

        self.outSel4 = ttk.Checkbutton(self.rConfig, variable=self.s4, text="Animation")
        self.outSel4["command"]= self.checkOverallValidity
        self.outSel4.grid(row=14, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)

        self.displayLabel = ttk.Label(self.rConfig, text="Should Display:")
        self.displayLabel.grid(row=10, column=5, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.dispSel1 = ttk.Radiobutton(self.rConfig, variable=self.displayMode, text="Component Graphs", value=0)
        self.dispSel1.grid(row=11, column=5, columnspan=2, sticky='W', padx=pVal, pady=pVal)
        self.dispSel1["command"] = self.assessDisplayMode
        self.dispSel1.state(["disabled"])

        self.dispSel2 = ttk.Radiobutton(self.rConfig, variable=self.displayMode, text="Parameterized Graph", value=1)
        self.dispSel2.grid(row=12, column=5, columnspan=2, sticky='W', padx=pVal, pady=pVal)
        self.dispSel2["command"] = self.assessDisplayMode
        self.dispSel2.state(["disabled"])

        self.dispSel3 = ttk.Radiobutton(self.rConfig, variable=self.displayMode, text="Animation", value=2)
        self.dispSel3.grid(row=13, column=5, columnspan=2, sticky='W', padx=pVal, pady=pVal)
        self.dispSel3["command"] = self.assessDisplayMode
        self.dispSel3.state(["disabled"])

        self.goButton = ttk.Button(self.rConfig, style="T.TButton")
        self.goButton["text"] = "Go"
        self.goButton["command"] = self.collectInputAndRun
        self.goButton.state(["disabled"])
        self.goButton.grid(row=15, column=0, columnspan=6, padx=pVal, pady=5)


        self.enterStructures = {
            "fileName":self.titleInput,
            "timeStep":self.timeStepInput,
            "eVal":self.eEnterA,
            "lVal":self.lEnterA,
            "rValA":self.rEnterA,
            "pValA":self.pEnterA,
            "urVal":self.urEnterB,
            "upVal":self.upEnterB,
            "rValB":self.rEnterB,
            "pValB":self.pEnterB
        }

        self.flipA()
        self.checkOverallValidity()

        return

    def findOutputPath(self, fileName, outType):
        realPath = grabTruePath(DEFAULT_SAVE_DIRS[outType] + fileName)
        return realPath

    def collectInputAndRun(self):
        self.rConfig.destroy()
        #self.rConfig.grab_release()

        self.progress = tk.Toplevel(takefocus=True)
        self.progress.title("Run In Progress")
        self.progress.grab_set()

        self.updateLabel = ttk.Label(self.progress, text="Collecting...")
        self.updateLabel.grid(row=0, column=0, sticky='W')

        self.bar = ttk.Progressbar(self.progress, mode='determinate',
            variable=self.workDone,
            orient=tk.HORIZONTAL,
            length=300)
        self.bar.grid(row=1, column=0, sticky='W')



        plotBaseName = self.fileNameToSave.get()
        dataName = plotBaseName + "_Data.dat"
        compPlotName = plotBaseName + "_Comp.png"
        paramPlotName = plotBaseName + "_Param.png"
        animName = plotBaseName + "_Anim.gif"

        dataOutPath = self.findOutputPath(dataName, "data")
        compOutPath = self.findOutputPath(compPlotName, "compPlot")
        paramOutPath = self.findOutputPath(paramPlotName, "paramPlot")
        animOutPath = self.findOutputPath(animName, "anim")


        tSteps = int(self.timeStepVal.get())

        sim = Simulator()

        self.updateLabel.config(text="Initializing Solver...")
        self.workDone.set(10)

        initialConditions = []

        if self.inputMode.get() == 0:
            e = float(self.eVal.get())
            l = float(self.lVal.get())

            isPositive = (False, True)[self.plusMinus.get()==1]

            r_i = float(self.rValA.get())
            p_i = float(self.pValA.get())

            initialConditions = sim.initcondgen(
                e,
                l,
                r_i,
                p_i,
                isPositive
            )


        if self.inputMode.get() == 1:
            ur = float(self.urEnterB.get())
            up = float(self.upEnterB.get())
            r_i = float(self.rValB.get())
            p_i = float(self.pValB.get())

            initialConditions = sim.initcondgen_ur_uw(ur, up, r_i, p_i)

        self.updateLabel.config(text="Simulating...")
        self.workDone.set(25)


        fieldNames = ["tau","r","phi","dt/dtau","dr/dtau","dphi/dtau"]

        sim.writeSolData(
            dataOutPath,
            initialConditions,
            np.linspace(0, tSteps, int(tSteps/DEFAULT_SIM_DELTA_TIME)),
            sim.Schwarzschild,
            fieldNames
            )

        self.updateLabel.config(text="Generating Plots...")
        self.workDone.set(50)


        tauUCode = u'\u03C4'
        phiUCode = u'\u03D5'
        dphi_dt_String = "d" + phiUCode + "/" "d" + tauUCode

        fNF = [
            tauUCode,
            'r',
            phiUCode,
            "dt/d" + tauUCode,
            "dr/d " + tauUCode,
            dphi_dt_String
            ]

        solData = sim.readSolData(dataOutPath)


        if self.s1.get() == 0:
            #Delete created data file
            try:
                os.remove(dataOutPath)
            except OSError:
                raise


        if self.s2.get() == 1:
            sim.plotSolData(
                solData,
                False,
                False,
                True,
                filename=compOutPath,
                plotTitle=plotBaseName,
                timeUnits="M",
                labels=fNF,
                yUnits=['M', 'M', "rad", "", "", "rad/M"]
            )

        if self.s3.get() == 1:
            solDatarray = solData[1]

            plotData = [
            [solData[0][0],
            solData[0][1],
            solData[0][4],
            solData[0][2]
            ],
            np.concatenate((solDatarray[:,0:2],solDatarray[:,4:5],solDatarray[:,2:3]),axis=1)
            ]

            fieldNamesRearranged = [fNF[0] ,fNF[1], fNF[4], fNF[2]]


            sim.plotSolData(
                plotData,
                True,
                False,
                True,
                filename=paramOutPath,
                plotTitle=plotBaseName,
                paramUnits=["M", "M"],
                dataNames=["r", "phi"],
                conversion=sim.paramConversion
            )

        self.updateLabel.config(text="Animating (this may take a while)...")
        self.workDone.set(75)

        if self.s4.get() == 1:
            solDatarray = solData[1]

            plotData = [
            [solData[0][0],
            solData[0][1],
            solData[0][4],
            solData[0][2]
            ],
            np.concatenate((solDatarray[:,0:2],solDatarray[:,4:5],solDatarray[:,2:3]),axis=1)
            ]

            fieldNamesRearranged = [fNF[0] ,fNF[1], fNF[4], fNF[2]]

            sim.makeAnimation(
                plotData,
                False,
                True,
                filename=animOutPath,
                animTitle=plotBaseName,
                dataNames=["r", "phi"],
                paramUnits=["M","M"],
                conversion=sim.paramConversion,
                frameSlice=int(np.ceil((tSteps/DEFAULT_SIM_DELTA_TIME)/500))
            )

        self.updateLabel.config(text="Cleaning Up...")
        self.workDone.set(90)

        self.updateLabel.config(text="Displaying...")
        self.workDone.set(95)

        if self.displayMode.get() == 0:
            self.loadFileFromPath(compOutPath)
        if self.displayMode.get() == 1:
            self.loadFileFromPath(paramOutPath)
        if self.displayMode.get() == 2:
            self.loadFileFromPath(animOutPath)

        self.updateLabel.config(text="Done")
        self.workDone.set(100)

        self.progress.destroy()
        #self.rConfig.grab_set()

        return


    def changeFrame(self, scaleValue):
        newFrame = int(scaleValue)
        self.currentFrame = newFrame
        self.setLabelFrame(self.currentFrame, self.allAnimFrames, self.animFrameNumber)
        return

    def update(self):
        #print("Updating")
        if self.isAnimLoaded and self.isPlaying:
            if self.currentFrame == self.animFrameNumber:
                self.currentFrame = 0
            self.master.after(
                int(np.ceil(self.FRAME_DELAY - 10)),
                self.setLabelFrame,
                self.currentFrame,
                self.allAnimFrames,
                self.animFrameNumber
                )
            self.gifScale.set(self.currentFrame)
            #print("Playing " + str(self.currentFrame))
            self.currentFrame += 1
        self.master.after(10, self.update)




def createWindow(geo, title, back):
    window = tk.Tk()
    #window.geometry(geo)
    window.title(title)
    window.configure(background=back)

    return window

root = createWindow("800x800", 'GR Orbit Simulator v0.9', 'black')
app = Application(master=root)
app.master.after(0, app.update)
app.mainloop()
