import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk, Image
from Solver import *
import os


DEFAULT_IMAGE = "Image_Assets/default.png"
PLAY_BUTTON_IMAGE = "Image_Assets/PlayButtonB.png"
PAUSE_BUTTON_IMAGE = "Image_Assets/PauseButtonB.png"
BACK_BUTTON_IMAGE = "Image_Assets/BackButtonB.png"
FORWARD_BUTTON_IMAGE = "Image_Assets/ForwardButtonB.png"

def grabTruePath(fileInDirectory):
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
    realPath = os.path.join(__location__, fileInDirectory)

    return realPath

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
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

        self.imagePanel = ttk.Label(self, image=defImg, style="BW.TLabel")
        self.imagePanel.image = defImg
        self.imagePanel.grid(row=0, column=0, columnspan=6)

        path = grabTruePath(BACK_BUTTON_IMAGE)
        bImg = ImageTk.PhotoImage(Image.open(path))
        self.backButton = ttk.Button(self, image=bImg, style="I.TButton")
        self.backButton.image = bImg
        self.backButton["command"] = self.animRestart
        self.backButton.grid(row=1, column=0, columnspan=3, sticky='E')

        path = grabTruePath(PLAY_BUTTON_IMAGE)
        playImg = ImageTk.PhotoImage(Image.open(path))
        path = grabTruePath(PAUSE_BUTTON_IMAGE)
        pauseImg = ImageTk.PhotoImage(Image.open(path))
        self.playButton = ttk.Button(self, image=playImg, style="I.TButton")
        self.playButton.image = (playImg, pauseImg)
        self.playButton["command"] = self.flipAnimPlayState
        self.playButton.grid(row=1, column=3)

        path = grabTruePath(FORWARD_BUTTON_IMAGE)
        fImg = ImageTk.PhotoImage(Image.open(path))
        self.forwardButton = ttk.Button(self, image=fImg, style="I.TButton")
        self.forwardButton.image = fImg
        self.forwardButton["command"] = self.animSkipToEnd
        self.forwardButton.grid(row=1, column=4, columnspan=3, sticky='W')


        self.outSelLabel = ttk.Label(self, text="Should Save:")
        self.outSelLabel.grid(row=2, column=0, sticky='W')

        self.outSel1 = ttk.Checkbutton(self, text="Data File")
        self.outSel1.grid(row=3, column=0, sticky='W')

        self.outSel2 = ttk.Checkbutton(self, text="Parameterized Graph")
        self.outSel2.grid(row=4, column=0, sticky='W')

        self.outSel2 = ttk.Checkbutton(self, text="Component Graphs")
        self.outSel2.grid(row=5, column=0, sticky='W')

        self.outSel2 = ttk.Checkbutton(self, text="Animation")
        self.outSel2.grid(row=6, column=0, sticky='W')

        self.inputRad1 = ttk.Radiobutton(
            self,
            text="Initial Conditions [" + u'\u2113' + ", e, r, " + u'\u03B8' + "]",
            value=0
            )
        self.inputRad1["command"] = self.flipA
        self.inputRad1.grid(row=2, column=1, columnspan=2)

        self.lEnterLabel = ttk.Label(self, text=u'\u2113')
        self.lEnterLabel.grid(row=3, column=1)
        self.lEnter = ttk.Entry(self)
        self.lEnter.grid(row=3, column=2)

        self.eEnterLabel = ttk.Label(self, text='e')
        self.eEnterLabel.grid(row=4, column=1)
        self.eEnter = ttk.Entry(self)
        self.eEnter.grid(row=4, column=2)

        self.rEnterLabel = ttk.Label(self, text='r')
        self.rEnterLabel.grid(row=5, column=1)
        self.rEnter = ttk.Entry(self)
        self.rEnter.grid(row=5, column=2)

        self.tEnterLabel = ttk.Label(self, text=u'\u03B8')
        self.tEnterLabel.grid(row=6, column=1)
        self.tEnter = ttk.Entry(self)
        self.tEnter.grid(row=6, column=2)

        self.inputRad2 = ttk.Radiobutton(
            self,
            text="Initial Conditions [v" + u'\u1D63' + ", v" + u'\u209C' + ", r, " + u'\u03B8' + "]",
            value=1)
        self.inputRad2["command"] = self.flipB
        self.inputRad2.grid(row=2, column=3, columnspan=2)

        self.vrEnterLabel = ttk.Label(self, text="v" + u'\u1D63')
        self.vrEnterLabel.grid(row=3, column=3)
        self.vrEnter = ttk.Entry(self)
        self.vrEnter.grid(row=3, column=4)

        self.vtEnterLabel = ttk.Label(self, text="v" + u'\u209C')
        self.vtEnterLabel.grid(row=4, column=3)
        self.vtEnter = ttk.Entry(self)
        self.vtEnter.grid(row=4, column=4)

        self.rEnterLabelB = ttk.Label(self, text='r')
        self.rEnterLabelB.grid(row=5, column=3)
        self.rEnterB = ttk.Entry(self)
        self.rEnterB.grid(row=5, column=4)

        self.tEnterLabelB = ttk.Label(self, text=u'\u03B8')
        self.tEnterLabelB.grid(row=6, column=3)
        self.tEnterB = ttk.Entry(self)
        self.tEnterB.grid(row=6, column=4)

        self.loadButton = ttk.Button(self, style="T.TButton")
        self.loadButton["text"] = "Load"
        self.loadButton["command"] = self.createPanel
        self.loadButton.grid(row=1, column=5, rowspan=3, sticky="E")

        self.runButton = ttk.Button(self, style="T.TButton")
        self.runButton["text"] = "Run"
        self.runButton["command"] = self.generate
        self.runButton.grid(row=4, column=5, rowspan=3, sticky="E")

        return

    #Sends an animation back to the beginning of its run time
    def animRestart(self):
        pass

    #Pauses or plays animation from last pause point depending on previous state
    #Also changes button appearance back and forth
    def flipAnimPlayState(self):
        pass

    #Skips to last frame of animation
    def animSkipToEnd(self):
        pass

    #Creates a pop-up window that asks the user to select the file to be loaded
    def createPanel(self):
        pass

    #Takes in window data and runs plotSolData() from Solver.py
    def generate(self):
        pass

    #Deactivates the B radio button's input and reactivates the A button's one
    def flipA(self):
        pass

    #Deactivates the A radio button's input and reactivates the B button's one
    def flipB(self):
        pass

def createWindow(geo, title, back):
    window = tk.Tk()
    #window.geometry(geo)
    window.title(title)
    window.configure(background=back)

    return window

root = createWindow("800x800", 'TestWindow', 'black')
app = Application(master=root)
app.mainloop()
