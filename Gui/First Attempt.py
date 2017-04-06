import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, qApp, QWidget, QListWidget, QListWidgetItem
from PyQt5 import uic, QtCore, QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy
import pyqtgraph as pg
import pandas as pd
import quandl
import cvxopt as cv
from cvxopt import blas

cv.solvers.options['show_progress'] = False
dbSchema = 'Stockdata'
quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"
token = 'p_qounXgMs57T9nYAurW'
start = '2015-01-01'

# Initialising all available stock data

#availableStockList = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'tsla', 'atvi']
availableStockList = ['ibm','aapl','msft','googl']

allData = pd.DataFrame([])
for stock in availableStockList:
    fullHolder = pd.DataFrame(quandl.get("WIKI/"+stock, trim_start = start, authtoken = token))
    closeHolder = pd.DataFrame(fullHolder['Adj. Close'])
    closeHolder.columns = [stock]
    if allData.empty:
        allData = closeHolder
    else:
        allData = allData.join(closeHolder, how='outer')
        

class Stock:
    def __init__(self,name):
        try:
            self.name = name
            self.Data = pd.DataFrame(allData[name])
            tempAdj = self.Data
            tempReturns = tempAdj.apply(lambda x: numpy.log(x) - numpy.log(x.shift(1)))
            tempReturns = tempReturns.rename(columns = {'Adj. Close' : self.name})
            tempReturns = tempReturns.fillna(value = 0)
            self.returns = tempReturns
            self.average = numpy.mean(self.returns)
            self.variance = numpy.var(self.returns)
            self.SD = numpy.std(self.returns)
        except Exception as e:
            print(e)

    def displayStats(self):
        try:
            print(self.name,"using data for 1 year:")
            print("Average Daily Return:", self.average,"%")
            print("Standard Deviation:", self.SD,"%")
            print("Variance:",self.variance,"%")
        except Exception as e:
            print(e)

availableStockObjects = {name: Stock(name=name) for name in availableStockList}
chosenStockList = []

# Defining the UI for each form #

Ui_MainWindow = uic.loadUiType("MainWindow.ui")[0]
Ui_StockChooser = uic.loadUiType("StockChooser.ui")[0]
Ui_StockPerformance = uic.loadUiType("StockPerformance.ui")[0]
Ui_StockAnalysis = uic.loadUiType("StockAnalysis.ui")[0]
 
# Main application window #

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)      
        self.ui.actionClose.triggered.connect(qApp.quit)
        self.ui.actionChoose_Stocks.triggered.connect(self.openStockChooser)
        self.ui.actionStock_Performance.triggered.connect(self.openStockPerformance)        
        self.ui.actionStock_Analysis.triggered.connect(self.openStockAnalysis)
        
    
    def openStockChooser(self):
        self.myStockChooser = StockChooser()
        self.myStockChooser.show()
    
    def openStockPerformance(self):
        self.myStockPerformance = StockPerformance()
        self.myStockPerformance.show()
    
    def openStockAnalysis(self):
        self.myStockAnalysis = StockAnalysis()
        self.myStockAnalysis.show()      
    
# Stock Chooser Form #

class StockChooser(QWidget):
    def __init__(self):
        super(StockChooser, self).__init__()
        self.ui = Ui_StockChooser()
        self.ui.setupUi(self)
        self.ui.saveAndCloseButton.clicked.connect(self.saveAndClose)
        #Populate the list with available stocks
        for stock in availableStockList:
            item = QListWidgetItem()
            item.setText(stock)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.ui.choiceList.addItem(item)
            
    def saveAndClose(self):
        chosenStockList = []        
        for index in range(self.ui.choiceList.count()):
            if self.ui.choiceList.item(index).checkState() == QtCore.Qt.Checked:            
               chosenStockList.append(self.ui.choiceList.item(index).text())
        print(chosenStockList)
        self.close()              
 
# Stock Performance Form #

class StockPerformance(QWidget):
    def __init__(self):
        super(StockPerformance, self).__init__()
        self.ui = Ui_StockPerformance()
        self.ui.setupUi(self)
        
# Stock Analysis Form #

class StockAnalysis(QWidget):
    def __init__(self):
        super(StockAnalysis, self).__init__()
        self.ui = Ui_StockAnalysis()
        self.ui.setupUi(self)       
        for stock in availableStockList:
            item = QListWidgetItem()
            item.setText(stock)
            self.ui.analysisChoice.addItem(item)
        self.ui.analysisChoice.itemClicked.connect(self.stockChose)
        
        
        y = numpy.asarray(availableStockObjects['ibm'].Data, dtype = numpy.float32)
      
        print(y)
        
        x = range(len(y))
        print(x)
        self.ui.adjCloseGraph.plot(x,y)       
        
#        fig1 = plt.figure()
#        ax1f1 = fig1.add_subplot(211)
#        ax1f1.plot(availableStockObjects['ibm'].Data)
#        ax1f2 = fig1.add_subplot(212)
#        ax1f2.plot(availableStockObjects['ibm'].returns)
#        dpi = fig1.get_dpi()
#        fig1.set_size_inches(590/float(dpi), 550/float(dpi))
#        self.createGraph(fig1)      
#        
#        
#    def createGraph(self, figure):
#        self.canvas = FigureCanvas(figure)        
#        self.ui.verticalLayout_2.addWidget(self.canvas)       
#        self.canvas.draw()
        
        
        
        
        
    def stockChose(self, item):
        #Setting analysis text
        
        text = item.text()     
        ret = str(round(availableStockObjects[text].average[0],6))
        var = str(round(availableStockObjects[text].variance[0],6))
        std = str(round(availableStockObjects[text].SD[0],6))
        self.ui.analysisText.setText("")
        self.ui.analysisText.setText("Average Return: " +ret+"%"+"\n\nVariance: "+var+"%"+"\n\nStandard Deviation: "+std+"%")
        
        #Plotting Adjusted Close Graph
        
        
        
       
        


        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())