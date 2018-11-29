import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import ImageMagickWriter
from matplotlib.collections import PatchCollection
import matplotlib.patches as pch


def dy_dx(y, x):
    return x - y


def dr_dt(t, r):
    r, gamma, theta = t
    drdt = np.array([gamma, -64 * (np.pi)**2 * (r - 1), np.pi])
    return drdt

def dtheta_dt(t, theta):
    return 1/(2 * np.pi)

'''
Reads ODE solution data from a file
################################################################################
filename -> File to read data from (file is not affected)
################################################################################
Return dOut -> A 2D array of the file's contents, separated by field
'''

class Simulator():

    def __init__(self):
        return None

################################################################################
# Schwarzschild Equations of Motion (1st order in tau; s=tau)
################################################################################

    def Schwarzschild(self,y,s,m=1): #y is the vector containing all the relevant variables, m is mass, s is a dummy variable(?)
        r, p, a, v, w = y #read vector; r is radius, p is phi, a is dt/dtau, v is dr/dtau, w is dphi/dtau
        d1 = v #first derivatives of r and phi respectively
        d2 = w
        d3 = (-2*m/(r**2))*((1-(2*m/r))**(-1))*v*a # these equations compute the second derivatives of t, r and phi
        #if np.absolute(d3) <= 0.000000001: #rectification for error slip
        #    d3 = 0
        d4 = (2*m/(r**2))*((1-(2*m/r))**-1)*(v**2)-(1-(2*m/r))*(m/(r**2))*(a**2)+r*(1-(2*m/r))*(w**2)
        #if np.absolute(d4) <= 0.000000001:
        #    d4 = 0
        d5 = (-2/r)*v*w
        #if np.absolute(d5) <= 0.000000001:
        #    d5 = 0
        if r == 0:
            print(s)
        dyds = [d1,d2,d3,d4,d5]
        return dyds

    def circlemaker(self,y,s,m=1):
        r,p,v,w = y
        d1 = 0
        d2 = w
        d3 = 0
        d4 = 0
        dyds = [d1,d2,d3,d4]
        return dyds


    def initcondgen(self,e,l,ri,pi,pos,m=1): #variable names are hopefully self explanatory, m included just in case we want to use it at some point
        i_cond = [0,0,0,0,0]
        i_cond[0] = ri
        i_cond[1] = pi
        sfactor = 1-2*m/ri
        ai = e/sfactor
        i_cond[2] = ai
        if pos == True:
            vi = np.sqrt(np.absolute(e**2-sfactor*(1+(l**2)/(ri**2))))
        else:
            vi = -np.sqrt(np.absolute(e**2-sfactor*(1+(l**2)/(ri**2))))
        if np.absolute(vi) <= 0.00001:
            vi = 0
        i_cond[3] = vi
        wi = l/(ri**2)
        i_cond[4] = wi
        return i_cond

    def initcondgen_ur_uw(self, ur, uw, ri, pi, m=1):
        i_cond = [0,0,0,0,0]
        i_cond[0] = ri
        i_cond[1] = pi

        vi = ur
        if np.absolute(vi) <= 0.00001:
            vi = 0
        i_cond[3] = vi

        wi = uw
        i_cond[4] = wi

        sfactor = 1-2*m/ri
        i_cond[2] = np.sqrt((1 + sfactor**(-1) * vi**2 + ri**2 * wi**2)/sfactor)

        return i_cond



    def readSolData(self,filename):
        #Get the header information from the very first line of the file, e.g., the
        #strings identifying the data to follow in each associated column
        header = [i for i in open(filename, 'r').readline().rstrip().split(",")]
        #Grab and reshape the second line of data from the file so we don't need to know
        #the actual number of fields we're taking in (WARNING: super hacky)
        dOut = np.array([float(i) for i in open(filename, 'r').read().split("\n")[1].rstrip().split(",")])
        #1 row, n columns where n is the number of values + 1 (for the independent variable)
        dOut = dOut.reshape((1, dOut.shape[0]))
        #Init the line to something generic but nonempty, will be overwritten anyway
        l = "0"
        hasSkipped = 0
        #Properly open the file for reading this time
        with open(filename, 'r') as file:
            #Until we reach the last line of the file
            while l != "":
                #Get the line and remove whitespace/newline characters
                l = file.readline().rstrip()
                #Make sure we skip the first, second and last lines so we don't include
                #them twice/at all, respectively
                if l != "" and hasSkipped > 1:
                    #Separate each field by the commas and make a new array of those
                    #values casted to floats
                    lineVals = np.array([float(i) for i in l.split(",")])
                    #Stick this new array onto the end of the output array to build
                    #up the full set of data, now separated by field
                    dOut = np.append(dOut, lineVals.reshape((1, lineVals.shape[0])), axis=0)
                #Change this after the first two loops so we don't accidentally skip
                #everything
                hasSkipped += 1
        #Return the full set of separated data, along with the header information
        return [header, dOut]

    '''
    Determines then writes the solution to the provided ODEs to a file
    ################################################################################
    filename -> Name of file to put the data in (cleared when accessed)
    initConditions -> Initial conditions for the solver
    indVals -> Range of independent variables values we'll step across when
        integrating the ode (e.g., timestep, in most cases)
    derivatives -> The actual ODE or system of ODE's we'll be solving
        (defined as functions somewhere else in this file, passed "by reference")
    axisNames -> A list of names by which each column will be identified in the
        output file; will serve as the header
    ################################################################################
    Return True -> Returns true if writing was successful
    '''
    def writeSolData(self,filename, initConditions, indVals, derivatives, axisNames,
        extraparams=[]):
        #extra params modify diffeq, input directly
        #Find the solution with helper method
        rVals = self.getSolData(initConditions, indVals, derivatives,extraparams)
        #Get the number of "timesteps" completed (rows) and the
        #number of value fields (columns) of the 2d output array
        steps, vals = rVals.shape
        #Open the file at filename for writing (deletes its previous contents)
        with open(filename, 'w') as file:

            for ind in range(vals + 1):
                if ind != vals:
                    file.write(axisNames[ind] + ",")
                else:
                    file.write(axisNames[ind] + "\n")
            #For each "timestep"
            for tIndex in range(steps):
                #write the "time" value as the first field in each row
                file.write(str(indVals[tIndex]))
                #For each additional value field
                for valIndex in range(vals):
                    #comma separate them then write the value
                    file.write("," + str(rVals[tIndex, valIndex]))
                #add a newline character to complete the line and advance the loop
                file.write("\n")
        #Return True if writing succeeded
        return True

    '''
    Helper method that actually does the integration for writeSolData()
    (for possible expansion later, currently fairly pointless)
    ################################################################################
    initConditions -> Initial conditions for the solver
    indVals -> Range of independent variables values we'll step across when
        integrating the ode (e.g., timestep, in most cases)
    derivatives -> The actual ODE or system of ODE's we'll be solving
        (defined as functions somewhere else in this file, passed "by reference")
    ################################################################################
    Returns the odeint() method's output for the given conditions/derivatives
    '''
    def getSolData(self,initConditions, indVals, derivatives,extraparams):
        return odeint(derivatives, initConditions, indVals)


    '''
    Default R^N to R^2 mapping for the plotSolData() method; truncates the passed
        array to include only the columns specified by their index in locs.
        Expected to be replaced by additional methods for any
        realistic application, but provides an example of what is necessary
    ################################################################################
    arr2 -> 2D (N, V) array containing some time and/or axis data
    locs -> A list of V' distinct indices of the columns containing the data we want
     to pass as output
    ################################################################################
    Return outArray -> A 2D (N, V') array that's mapped the V columns of the input
        array to V' in the output array, in this case simply by truncation
    '''
    def defaultConversion(arr2, locs):
        row = np.array([])
        outArray = np.empty((1, len(locs)))
        for index in range(arr2.shape[0]):
            #Append the same first-two-column-slice as additional rows of the
            #output array.
            #In an actual application, this row would be replaced by the desired
            #coordinate conversion between the V elements and Cartesian coordinates.
            for val in range(len(locs)):
                row.append(arr2[index, val])
            outArray = np.append(outArray, val.reshape((1, val.shape[1])), axis=0)
            row = np.array([])
        #Return the now (N, V') mapped array as the output, snipping the first
        #empty row to avoid weird data effects
        return outArray[1:, :]


    '''
    Maps the input from 2D polar to 2D Cartesian input, via the standard r * cos(th)
        and r * sin(th) transformations, using the same general methodology as in
        the default version
    ################################################################################
    arr2 -> 2D (N, V) array containing some time and/or axis data
    locs -> A list containing at least two indices, specifying the locations of the
        r and theta columns in arr2 for access
    ################################################################################
    '''
    def paramConversion(self,arr2, locs):
        outArray = np.empty((1, len(locs)))
        for index in range(arr2.shape[0]):
            x = arr2[index, locs[0]] * np.cos(arr2[index, locs[1]])
            y = arr2[index, locs[0]] * np.sin(arr2[index, locs[1]])
            outArray = np.append(outArray, np.array([x, y]).reshape((1, 2)), axis=0)
        return outArray[1:, :]
    '''
    Main plotting method that creates, saves, and displays plots of provided data
    ***Restricted to 2D plots at the moment***
    ################################################################################
    allData -> A list containing at index [0] the names of each data field, and at
        index [1] a 2D Array of all associated values of those "timesteps" data
        fields; rows = values for each timestep, columns = values for each field
        therein
    shouldParameterize -> Should we make a parametric plot, or plot each field
        separately?
    shouldShow -> Should we immediately display the created plots?
    shouldSave -> Should we save the created plots?
    filename -> If shouldSave is True, then the created plots will go here.
    plotTitle -> Title of the plot to be created
    timeUnits -> Units for the x or "timestep" axis if shouldParameterize is False
    labels -> List of value-field axis labels, defaults to basic alphabetical
    yUnits -> List of corresponding units for those labels, defaults to "meters"
    paramUnits -> List of axis units to use for a parameterized plot
    dataNames -> List of header names that the conversion will use to map data;
        identifies the appropriate column in fullArray
    conversion -> If shouldParameterize is True, this is the mapping between the R^N
        "time" and value fields and the R^2 x, y Cartesian coordinates we'll plot
        with; like the ODE equations is a method defined somewhere else, passed
        "by reference." Defaults to truncation of 2+N value fields, passing the
        first two non-timestep fields as x and y directly.
    ################################################################################
    Return True -> Returns true if the plotting, saving, and/or displaying succeeded
    '''

    def ehcircle(self,m=1): #makes a circle at the Schwarzschild radius for visualization purposes
        iconds = [2*m,0,0,np.pi/200] #r=2m, phi = 0, dr/dt = 0, frequency = whatever makes it smooth and a full circle
        self.writeSolData(
                "EHcircle.dat",
                iconds,
                np.linspace(0,400,400), #2pi/omega
                self.circlemaker,
                ["t", "r", "phi","dr_dt", "dp_dt"]
                )
        return None

    def plotSolData(self,allData, shouldParameterize, shouldShow, shouldSave,
     filename = "defaultFilename.png",
     plotTitle = "Output",
     timeUnits="seconds",
     labels=[chr(i) for i in range(97,123,1)],
     yUnits=[None],
     paramUnits = ["meters", "meters"],
     dataNames=["x", "y"],
     conversion=defaultConversion,
     showEH=True):

        names = allData[0]
        fullArray = allData[1]

        #Grab the timesteps into their own array for convenient access later
        tSteps = fullArray[:, 0]

        #If we should make a parametric plot
        if shouldParameterize:

            fig, ax = plt.subplots(figsize=(5,5))
            ax.set_aspect(1)

            #Find the column location in fullArray of the data we want to use
            locs = [names.index(name) for name in dataNames]
            #Get the x and y arrays using our specified conversion by passing
            #the "coordinate" value fields into it, effectively transforming our
            #data into a path in Cartesian coordinates
            out = conversion(fullArray[:, :], locs)
            x = out[:, 0]
            y = out[:, 1]
            #Title the plot
            ax.set_title(plotTitle)
            #Label the x and y axes "x (units)", "y (units)"
            ax.set_xlabel("x (" + paramUnits[0] + ")")
            ax.set_ylabel("y (" + paramUnits[1] + ")")
            #Plot the x values versus the y values, which will implicitly be parametric
            ax.plot(x, y)

            if showEH:
                circle = pch.Circle((0,0),radius=2,color='black')
                ax.add_patch(circle)

                """
                #me overthinking things
                try:
                    circledata = self.readSolData("EHcircle.dat")
                except:
                    self.ehcircle()
                    circledata = self.readSolData("EHcircle.dat")
                circleArray = circledata[1]
                circleout = self.paramConversion(circleArray[:,:],[1,2])
                xc = circleout[:,0]
                yc = circleout[:,1]
                plt.plot(xc,yc)
                """
        #If we're not making parametric plots
        else:
            #Get the size of the "coordinate" fields in the input array
            n = fullArray.shape[1] - 1
            #Title the overall plot
            plt.title(plotTitle)
            #Generate default unit labels for each axis if none were given
            if yUnits[0] == None:
                yUnits = ["meters" for i in range(n)]
            #For each coordinate field, we will make additional subplots which will
            #automatically be composited into a single larger one for ease of
            #saving and display
            for axis in range(1,n):

                #Make a new subplot in the (n, 1) grid (e.g., successive axes will
                #move downwards)
                plt.subplot(n, 1, axis)
                #Label the x-axis as time
                plt.xlabel(u'\u03C4' +  " (" + timeUnits + ")")
                #and the y-axis as whatever the name of the coordinate is
                if yUnits[axis] != "":
                    plt.ylabel(labels[axis-1] + " (" + yUnits[axis-1] + ")")
                else:
                    plt.ylabel(labels[axis-1])
                #Then plot it with x using the timestep data and y using the
                #coordinate data for that axis
                plt.plot(tSteps, fullArray[:, axis + 1])

            #Space out axes at the end so the x-labels don't overlap with the graph below
            plt.subplots_adjust(hspace=1.5)
        #If we should save the plot, write the resulting plot to the given filename
        if shouldSave:
            plt.savefig(filename)
        #If we should show the plot, display it
        if shouldShow:
            plt.show()

        #Return True if plot generation was successful
        return True

    def makeAnimation(self,
        allData,
        shouldShow,
        shouldSave,
        dataNames=["x", "y"],
        conversion=defaultConversion,
        paramUnits = ["meters", "meters"],
        filename = 'defaultFilename.gif',
        animTitle = "Output",
        boundScale = 1.3,
        animSpeed = 1,
        frameSlice = 10
        ):

        names = allData[0]
        fullArray = allData[1]

        tSteps = fullArray[:, 0].flatten()

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_aspect(1)

        locs = [names.index(name) for name in dataNames]
        out = conversion(fullArray[:, :], locs)

        ax.set_xlabel("x" + "(" + paramUnits[0]  + ")")
        ax.set_ylabel("y" + "(" + paramUnits[1] +  ")")

        x = out[:, 0].flatten()
        y = out[:, 1].flatten()

        xMin = boundScale * np.amin(x)
        xMax = boundScale * np.amax(x)

        yMin = boundScale * np.amin(y)
        yMax = boundScale * np.amax(y)

        ax.set(xlim=(xMin, xMax), ylim=(yMin, yMax))

        circle = pch.Circle((0,0),radius=2,color='black')
        ax.add_patch(circle)

        line = ax.plot(x[0], y[0], color='b', lw=2)[0]

        anim = FuncAnimation(
        fig,
        lambda i: line.set_data(x[:i:frameSlice], y[:i:frameSlice]),
        frames=len(x)-1
        )

        if shouldShow:
            plt.show()

        if shouldSave:
            #Framerate of produced gif is ~1/10 the fps actually specified,
            #no idea why; optimizing for 60 Hz display
            anim.save(filename, writer="pillow", fps=600)

        print("Animation Complete")

        return True

################################################################################
# For command-line interaction (entry into the program is below)
################################################################################
'''
Test = Simulator()
Test.writeSolData(
    "test.dat",
    [1.2, 0, 0],
    np.linspace(0,2,2000),
    dr_dt,
    ["t", "r", "dr_dt", "theta"]
    )
solData = Test.readSolData("test.dat")

Test.plotSolData(
    solData,
    True,
    True,
    True,
    filename = "paramTest.png",
    yUnits=["m/s", "m", "rads"],
    labels=["r", "dr/dt", "theta"],
    dataNames=["r", "theta"],
    conversion=Test.paramConversion
    )

Test.makeAnimation(
    solData,
    False,
    True,
    dataNames=["r", "theta"],
    conversion=Test.paramConversion,
    filename="test.gif"
    )


'''
##############################################################################
# Schwarzschild interaction test
##############################################################################
'''
#ISCO test
iscotest = Simulator()
iscotest.writeSolData(
    "iscotest.dat",
    [6,0,1.5,0,1.5/(6*np.sqrt(6))],
    np.linspace(0,100,10000),
    iscotest.Schwarzschild,
    ["tau","r","phi","dt/dtau","dr/dtau","dphi/dtau"]
    )
solData = iscotest.readSolData("iscotest.dat")
print(solData)
solDatarray = solData[1]

plotdata = [[solData[0][0],solData[0][1],solData[0][4],solData[0][2]],np.concatenate((solDatarray[:,0:2],solDatarray[:,4:5],solDatarray[:,2:3]),axis=1)]
print(plotdata)

iscotest.plotSolData(
    plotdata,
    True,
    True,
    True,
    filename = "iscoTest.png",
    yUnits=["m/s", "m", "rads"],
    labels=["r", "dr/dt", "theta"],
    dataNames=["r", "phi"],
    conversion=iscotest.paramConversion
    )

#general test

gentest = Simulator()
iconds = gentest.initcondgen(.97,4.3,30,0,False)

gentest.writeSolData(
    "gentest.dat",
    iconds,
    np.linspace(0,2000,10000), #how do we guarantee these are the right values?)
    gentest.Schwarzschild,
    ["tau","r","phi","dt/dtau","dr/dtau","dphi/dtau"]
    )
solData = gentest.readSolData("gentest.dat")
solDatarray = solData[1]

plotdata = [[solData[0][0],solData[0][1],solData[0][4],solData[0][2]],np.concatenate((solDatarray[:,0:2],solDatarray[:,4:5],solDatarray[:,2:3]),axis=1)]

gentest.plotSolData(
    plotdata,
    True,
    True,
    True,
    filename = "genTest.png",
    yUnits=["m/s", "m", "rads"],
    labels=["r", "dr/dt", "theta"],
    dataNames=["r", "phi"],
    conversion=gentest.paramConversion
    )

gentest.makeAnimation(
    plotdata,
    False,
    True,
    dataNames=["r", "phi"],
    conversion=gentest.paramConversion,
    filename="test.gif"
    )









'''








