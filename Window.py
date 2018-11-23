import numpy as np
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from PIL import ImageTk, Image
from Solver import *
import os


DEFAULT_IMAGE = "Image_Assets/default.png"
PLAY_BUTTON_IMAGE = "Image_Assets/PlayButtonB.png"
PAUSE_BUTTON_IMAGE = "Image_Assets/PauseButtonB.png"
BACK_BUTTON_IMAGE = "Image_Assets/BackButtonB.png"
FORWARD_BUTTON_IMAGE = "Image_Assets/ForwardButtonB.png"

DEFAULT_OPEN_DIR = "Output\\"

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

        self.inputMode = tk.IntVar(value=0)

        self.displayMode = tk.IntVar(value=0)


        self.s1 = tk.IntVar(value=0)
        self.s2 = tk.IntVar(value=0)
        self.s3 = tk.IntVar(value=0)
        self.s4 = tk.IntVar(value=0)

        self.master = master
        self.pack()
        self.configStyles()
        self.createWidgets()

    def configStyles(self):
        style = ttk.Style()
        style.configure("T.TButton", foreground="black", background="grey")
        style.configure("I.TButton", foreground="white", background="white")
        style.configure("BW.TLabel", foreground="white", background="black")
        return


    def createWidgets(self):
        path = grabTruePath(DEFAULT_IMAGE)
        defImg = ImageTk.PhotoImage(Image.open(path))

        self.columnconfigure(2)

        pVal = 4

        self.plotLabel = ttk.Label(self, text="Currently Displaying: None")
        self.plotLabel.grid(row=0, column=0, columnspan=7, padx=16)

        self.imagePanel = ttk.Label(self, image=defImg, style="BW.TLabel")
        self.imagePanel.image = defImg
        self.imagePanel.grid(row=1, column=0, columnspan=7, padx=16)

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

        self.containerFrame.grid(row=2, column=0, columnspan=7)

        self.loadButton = ttk.Button(self, style="T.TButton")
        self.loadButton["text"] = "Load"
        self.loadButton["command"] = self.loadFileFromDialog
        self.loadButton.grid(row=3, column=0, sticky="W")

        self.runButton = ttk.Button(self, style="T.TButton")
        self.runButton["text"] = "Simulate"
        self.runButton["command"] = self.generate
        self.runButton.grid(row=3, column=6, sticky="E")

        return

    #Sends an animation back to the beginning of its run time
    def animRestart(self):
        self.currentFrame = 0
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

                self.setLabelFrame(0, self.allAnimFrames, self.animFrameNumber)


            else:
                if '.png' in filePath:
                    self.isAnimLoaded = False

                    self.backButton.state(["disabled"])
                    self.playButton.state(["disabled"])
                    self.forwardButton.state(["disabled"])

                    self.animFrameNumber = -1

                    img = ImageTk.PhotoImage(Image.open(filePathToLoad))
                    self.imagePanel["image"] = img
                    self.imagePanel.image = img

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

        if success:
            self.plotLabel["text"] = "Currently Displaying: " + filePathToLoad.split("/")[-1]

        return success

    #Displays pop-up window that lets the user configure the run
    def generate(self):
        top = tk.Toplevel(takefocus=True)
        top.title("Configure Run")
        #top.config(background='gray50')
        top.grab_set()

        pVal = 2

        self.instruct = ttk.Label(top, text="Enter Run Parameters")
        self.instruct.grid(row=0, column=0, columnspan=4, padx=pVal, pady=pVal)

        self.titleInputLabel = ttk.Label(top, text="Run Name:")
        self.titleInputLabel.grid(row=1, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)
        self.titleInput = ttk.Entry(top)
        self.titleInput.grid(row=2, column=0, columnspan=4, sticky='W', padx=pVal, pady=pVal)



        self.inputRad1 = ttk.Radiobutton(
            top,
            text="Initial Conditions [" + u'\u2113' + ", e, r, " + u'\u03D5' + "]",
            variable=self.inputMode,
            value=0
            )
        self.inputRad1["command"] = self.flipA
        self.inputRad1.grid(row=3, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.lEnterLabelA = ttk.Label(top, text=u'\u2113')
        self.lEnterLabelA.grid(row=4, column=0, sticky='W', padx=pVal, pady=pVal)
        self.lEnterA = ttk.Entry(top)
        self.lEnterA.grid(row=4, column=1, sticky='W', padx=pVal, pady=pVal)

        self.eEnterLabelA = ttk.Label(top, text='e')
        self.eEnterLabelA.grid(row=5, column=0, sticky='W', padx=pVal, pady=pVal)
        self.eEnterA = ttk.Entry(top)
        self.eEnterA.grid(row=5, column=1, sticky='W', padx=pVal, pady=pVal)

        self.rEnterLabelA = ttk.Label(top, text='r')
        self.rEnterLabelA.grid(row=6, column=0, sticky='W', padx=pVal, pady=pVal)
        self.rEnterA = ttk.Entry(top)
        self.rEnterA.grid(row=6, column=1, sticky='W', padx=pVal, pady=pVal)

        self.pEnterLabelA = ttk.Label(top, text=u'\u03D5')
        self.pEnterLabelA.grid(row=7, column=0, sticky='W', padx=pVal, pady=pVal)
        self.pEnterA = ttk.Entry(top)
        self.pEnterA.grid(row=7, column=1, sticky='W', padx=pVal, pady=pVal)



        self.inputRad2 = ttk.Radiobutton(
            top,
            text="Initial Conditions [v" + u'\u1D63' + ", v" + u'\u209A' + ", r, " + u'\u03D5' + "]",
            variable=self.inputMode,
            value=1)

        self.inputRad2["command"] = self.flipB
        self.inputRad2.grid(row=3, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.vrEnterLabelB = ttk.Label(top, text="v" + u'\u1D63')
        self.vrEnterLabelB.grid(row=4, column=2, sticky='W', padx=pVal, pady=pVal)
        self.vrEnterB = ttk.Entry(top)
        self.vrEnterB.grid(row=4, column=3, sticky='W', padx=pVal, pady=pVal)

        self.vtEnterLabelB = ttk.Label(top, text="v" + u'\u209A')
        self.vtEnterLabelB.grid(row=5, column=2, sticky='W', padx=pVal, pady=pVal)
        self.vtEnterB = ttk.Entry(top)
        self.vtEnterB.grid(row=5, column=3, sticky='W', padx=pVal, pady=pVal)

        self.rEnterLabelB = ttk.Label(top, text='r')
        self.rEnterLabelB.grid(row=6, column=2, sticky='W', padx=pVal, pady=pVal)
        self.rEnterB = ttk.Entry(top)
        self.rEnterB.grid(row=6, column=3, sticky='W', padx=pVal, pady=pVal)

        self.pEnterLabelB = ttk.Label(top, text=u'\u03D5')
        self.pEnterLabelB.grid(row=7, column=2, sticky='W', padx=pVal, pady=pVal)
        self.pEnterB = ttk.Entry(top)
        self.pEnterB.grid(row=7, column=3, sticky='W', padx=pVal, pady=pVal)


        self.outSelLabel = ttk.Label(top, text="Should Save:")
        self.outSelLabel.grid(row=8, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.outSel1 = ttk.Checkbutton(top, variable=self.s1, text="Data File")
        self.outSel1.grid(row=9, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.outSel2 = ttk.Checkbutton(top, variable=self.s2, text="Parameterized Graph")
        self.outSel2.grid(row=10, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.outSel3 = ttk.Checkbutton(top, variable=self.s3, text="Component Graphs")
        self.outSel3.grid(row=11, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.outSel4 = ttk.Checkbutton(top, variable=self.s4, text="Animation")
        self.outSel4.grid(row=12, column=0, columnspan=2, sticky='W', padx=pVal, pady=pVal)



        self.displayLabel = ttk.Label(top, text="Should Display:")
        self.displayLabel.grid(row=8, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.dispSel1 = ttk.Radiobutton(top, variable=self.displayMode, text="Component Graphs", value=0)
        self.dispSel1.grid(row=9, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.dispSel2 = ttk.Radiobutton(top, variable=self.displayMode, text="Parameterized Graph", value=1)
        self.dispSel2.grid(row=10, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.dispSel3 = ttk.Radiobutton(top, variable=self.displayMode, text="Animation", value=2)
        self.dispSel3.grid(row=11, column=2, columnspan=2, sticky='W', padx=pVal, pady=pVal)

        self.goButton = ttk.Button(top, style="T.TButton")
        self.goButton["text"] = "Go"
        self.goButton["command"] = self.collectInputAndRun
        self.goButton.grid(row=13, column=0, columnspan=4, padx=pVal, pady=5)

        self.flipA()

        return

    #Deactivates the B radio button's input and reactivates the A button's one
    def flipA(self):
        self.lEnterA.state(["!disabled"])
        self.eEnterA.state(["!disabled"])
        self.rEnterA.state(["!disabled"])
        self.pEnterA.state(["!disabled"])

        self.vrEnterB.state(["disabled"])
        self.vtEnterB.state(["disabled"])
        self.rEnterB.state(["disabled"])
        self.pEnterB.state(["disabled"])

        return

    #Deactivates the A radio button's input and reactivates the B button's one
    def flipB(self):
        self.vrEnterB.state(["!disabled"])
        self.vtEnterB.state(["!disabled"])
        self.rEnterB.state(["!disabled"])
        self.pEnterB.state(["!disabled"])

        self.lEnterA.state(["disabled"])
        self.eEnterA.state(["disabled"])
        self.rEnterA.state(["disabled"])
        self.pEnterA.state(["disabled"])

        return

    def collectInputAndRun(self):
        pass

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
            #print("Playing " + str(self.currentFrame))
            self.currentFrame += 1
        self.master.after(10, self.update)




def createWindow(geo, title, back):
    window = tk.Tk()
    #window.geometry(geo)
    window.title(title)
    window.configure(background=back)

    return window

root = createWindow("800x800", 'TestWindow', 'black')
app = Application(master=root)
app.master.after(0, app.update)
app.mainloop()
