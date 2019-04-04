'''Heat conduction for meat in a kiln or similar enclosed surface
by Zong Lam
Last changed 4/4/19'''

#Import necessary modules
import numpy #For math
from PyQt5 import QtWidgets #For GUI
from simulationUI import Ui_MainWindow #For GUI setup code
import sys

'''Constant Properties for each Meat'''
#Salmon
SALMON_SAFE_TEMP = 336                  #K, USDA recommendation
SALMON_SPECIFIC_HEAT = 3600             #J/kg*K from https://vtechworks.lib.vt.edu/handle/10919/36834 (Radhakrishnan, Sudhaharini. Measurement of thermal properties of seafood. Diss. Virginia Tech, 1997.)
SALMON_THERMAL_CONDUCTIVITY = .4711     #W/m*k from https://vtechworks.lib.vt.edu/handle/10919/36834 (Radhakrishnan, Sudhaharini. Measurement of thermal properties of seafood. Diss. Virginia Tech, 1997.)
SALMON_DENSITY = 1037.41                #kg/m3 from https://www.aqua-calc.com/calculate/food-volume-to-weight

#Chicken
CHICKEN_SAFE_TEMP = 347                 #K, USDA recommendation
CHICKEN_SPECIFIC_HEAT = 3560            #J/kg*K
CHICKEN_THERMAL_CONDUCTIVITY = .476     #W/m*k
CHICKEN_DENSITY = 1050                  #kg/m3

#Beef - all data from Heat Transfer: A Practical Approach 2nd Ed. by Yunus A. Cengel - Appendix A.7
BEEF_SAFE_TEMP = 344                #K, USDA recommendation
BEEF_SPECIFIC_HEAT = 3540           #J/kg*K
BEEF_THERMAL_CONDUCTIVITY = .471    #W/m*k
BEEF_DENSITY = 1090                 #kg/m3

#Pork - all data from Heat Transfer: A Practical Approach 2nd Ed. by Yunus A. Cengel - Appendix A.7
PORK_SAFE_TEMP = 344                #K, USDA recommendation
PORK_SPECIFIC_HEAT = 3490           #J/kg*K
PORK_THERMAL_CONDUCTIVITY = .456    #W/m*k
PORK_DENSITY = 1030                 #kg/m3

#Lamb - all data from Heat Transfer: A Practical Approach 2nd Ed. by Yunus A. Cengel - Appendix A.7
VEAL_SAFE_TEMP = 344                #K, USDA recommendation
VEAL_SPECIFIC_HEAT = 3560           #J/kg*K
VEAL_THERMAL_CONDUCTIVITY = .470    #W/m*k
VEAL_DENSITY = 1060                 #kg/m3

'''Problem Setup/Execution'''
def simulate(height, length, temp, cookedTemp, capacity, conductivity, density):
    
    '''Initial Conditions'''
    initialTemp = 273           #K, assumed at 273.15K as food is frozen
    surfaceTemp = temp          #K, assumed that surface is same temperature as oven/kiln
    
    '''Geometry'''
    Y = height #m
    X = length #m
    dX = .001 #m, change in x
    dY = .001 #m, change in y
    dX2 = dX*dX
    dY2 = dY*dY
    nY = int(Y / dY)
    nX = int(X / dX)
    
    '''Thermophysical Properties'''
    diffusivity = (conductivity/(density*capacity))
    print(diffusivity)
    
    '''Populate Array'''
    T0 = initialTemp * numpy.ones((nX,nY))
    T = numpy.empty((nX, nY))
    for i in range(nX):
        for j in range(nY):
            T0[i,j] = initialTemp
    dt = dX2 * dY2 / (2 * diffusivity * (dX2 + dY2))
    
    '''Simulation - step by step through'''
    def simulateStep(T0, T):
        T[1:-1, 1:-1] = T0[1:-1, 1:-1] + diffusivity * dt * ((T0[2:, 1:-1] - 2*T0[1:-1, 1:-1] + T0[:-2, 1:-1])/dX2 + (T0[1:-1, 2:] - 2*T0[1:-1, 1:-1] + T0[1:-1, :-2])/dY2 )
        T0 = T.copy()
        T[0] = surfaceTemp
        T[nX-1] = surfaceTemp
        T[:, 0] = surfaceTemp
        T[:, nY-1] = surfaceTemp
        return T0, T
    
    tempBelow = True
    timesSimulated = 0
    while tempBelow == True:
        T0, T = simulateStep(T0, T)
        #print(T[int(nX/2) ,int(nY/2)])
        #print(timesSimulated)
        if T[int(nX/2) ,int(nY/2)] >= cookedTemp:
            tempBelow = False
        timesSimulated += 1
    print(dt*timesSimulated, "seconds, or", dt*timesSimulated/60, "minutes.")
    timeToCook = str(numpy.around((dt*timesSimulated/60), decimals = 2))
    formatted = timeToCook + " minutes!"
    mainWindow.timeToCookLabel.setText(formatted)
    
class ApplicationWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(ApplicationWindow, self).__init__(parent)
        self.setupUi(self)
        self.ovenTemperature = 350
        self.heightFood = 5
        self.lengthFood = 5
        self.safeTemp = CHICKEN_SAFE_TEMP
        self.specificHeat = CHICKEN_SPECIFIC_HEAT
        self.thermalConductivity = CHICKEN_THERMAL_CONDUCTIVITY
        self.density = CHICKEN_DENSITY
        self.calculateButton.clicked.connect(self.calculate)
        self.meatLengthSlider.valueChanged['int'].connect(self.updateLength)
        self.meatThicknessSlider.valueChanged['int'].connect(self.updateWidth)
        self.ovenTempSlider.valueChanged['int'].connect(self.updateTemp)
        self.meatSelector.activated[str].connect(self.changeMeat)

    def calculate(self):
        print ("BEGIN CALCULATION")
        lengthMeters = self.lengthFood / 100
        print(lengthMeters)
        heightMeters = self.heightFood / 100
        print(heightMeters)
        ovenKelvin = int((self.ovenTemperature+459.67) * (5/9))
        print(ovenKelvin)
        simulate(lengthMeters, heightMeters, ovenKelvin, self.safeTemp, self.specificHeat,self.thermalConductivity, self.density)
        print("CALCULATION FINISHED")
    def updateLength(self, value):
        self.lengthFood = value
        print(self.lengthFood)
    def updateWidth(self, value):
        self.heightFood = value
        print(self.heightFood)
    def updateTemp(self, value):
        self.ovenTemperature = value
        print(self.ovenTemperature)
    def changeMeat(self, text):
        print("Selection changed to", text)
        if text in "Salmon":
            self.safeTemp = SALMON_SAFE_TEMP
            self.specificHeat = SALMON_SPECIFIC_HEAT
            self.thermalConductivity = SALMON_THERMAL_CONDUCTIVITY
            self.density = SALMON_DENSITY
            print("Properties changed to salmon")
        if text in "Chicken":
            self.safeTemp = CHICKEN_SAFE_TEMP
            self.specificHeat = CHICKEN_SPECIFIC_HEAT
            self.thermalConductivity = CHICKEN_THERMAL_CONDUCTIVITY
            self.density = CHICKEN_DENSITY
            print("Properties changed to chicken")
        if text in "Beef (Lean)":
            self.safeTemp = BEEF_SAFE_TEMP
            self.specificHeat = BEEF_SPECIFIC_HEAT
            self.thermalConductivity = BEEF_THERMAL_CONDUCTIVITY
            self.density = BEEF_DENSITY
            print("Properties changed to beef (lean)")
        if text in "Pork (Lean)":
            self.safeTemp = PORK_SAFE_TEMP
            self.specificHeat = PORK_SPECIFIC_HEAT
            self.thermalConductivity = PORK_THERMAL_CONDUCTIVITY
            self.density = PORK_DENSITY
            print("Properties changed to pork (lean)")
        if text in "Veal":
            self.safeTemp = VEAL_SAFE_TEMP
            self.specificHeat = VEAL_SPECIFIC_HEAT
            self.thermalConductivity = VEAL_THERMAL_CONDUCTIVITY
            self.density = VEAL_DENSITY
            print("Properties changed to veal (lean)")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = ApplicationWindow()
    mainWindow.show()
    sys.exit(app.exec_())
