import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt


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
def readSolData(filename):
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
def writeSolData(filename, initConditions, indVals, derivatives, axisNames):
    #Find the solution with helper method
    rVals = getSolData(initConditions, indVals, derivatives)
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
def getSolData(initConditions, indVals, derivatives):
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
def paramConversion(arr2, locs):
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
def plotSolData(allData, shouldParameterize, shouldShow, shouldSave,
 filename = "defaultFilename.png",
 plotTitle = "Output",
 timeUnits="seconds",
 labels=[chr(i) for i in range(97,123,1)],
 yUnits=[""],
 paramUnits = ["meters", "meters"],
 dataNames=["x", "y"],
 conversion=defaultConversion):

    names = allData[0]
    fullArray = allData[1]

    #Grab the timesteps into their own array for convenient access later
    tSteps = fullArray[:, 0]

    #If we should make a parametric plot
    if shouldParameterize:
        #Find the column location in fullArray of the data we want to use
        locs = [names.index(name) for name in dataNames]
        #Get the x and y arrays using our specified conversion by passing
        #the "coordinate" value fields into it, effectively transforming our
        #data into a path in Cartesian coordinates
        out = conversion(fullArray[:, :], locs)
        x = out[:, 0]
        y = out[:, 1]
        #Title the plot
        plt.title(plotTitle)
        #Label the x and y axes "x (units)", "y (units)"
        plt.xlabel("x (" + paramUnits[0] + ")")
        plt.ylabel("y (" + paramUnits[1] + ")")
        #Plot the x values versus the y values, which will implicitly be parametric
        plt.plot(x, y)
    #If we're not making parametric plots
    else:
        #Get the size of the "coordinate" fields in the input array
        n = fullArray.shape[1] - 1
        #Title the overall plot
        plt.title(plotTitle)
        #Generate default unit labels for each axis if none were given
        if yUnits[0] == "":
            yUnits = ["meters" for i in range(n)]
        #For each coordinate field, we will make additional subplots which will
        #automatically be composited into a single larger one for ease of
        #saving and display
        for axis in range(n):

            #Make a new subplot in the (n, 1) grid (e.g., successive axes will
            #move downwards)
            plt.subplot(n, 1, axis + 1)
            #Label the x-axis as time
            plt.xlabel("Time (" + timeUnits + ")")
            #and the y-axis as whatever the name of the coordinate is
            plt.ylabel(labels[axis - 1] + " (" + yUnits[axis - 1] + ")")

            #Then plot it with x using the timestep data and y using the
            #coordinate data for that axis
            plt.plot(tSteps, fullArray[:, axis + 1])

        #Space out axes at the end so the x-labels don't overlap with the graph below
        plt.subplots_adjust(hspace=0.75)

    #If we should save the plot, write the resulting plot to the given filename
    if shouldSave:
        plt.savefig(filename)
    #If we should show the plot, display it
    if shouldShow:
        plt.show()

    #Return True if plot generation was successful
    return True


################################################################################
# For command-line interaction (entry into the program is below)
################################################################################
'''
writeSolData(
    "test.dat",
    [1.2, 0, 0],
    np.linspace(0,2,2000),
    dr_dt,
    ["t", "r", "dr_dt", "theta"]
    )
solData = readSolData("test.dat")
plotSolData(
    solData,
    True,
    True,
    True,
    filename = "paramTest.png",
    yUnits=["m/s", "m", "rads"],
    labels=["r", "dr/dt", "theta"],
    dataNames=["r", "theta"],
    conversion=paramConversion
    )
'''
################################################################################

