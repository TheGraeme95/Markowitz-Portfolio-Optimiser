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
start = '2016-01-01'

# Initialising all available stock data

availableStockList = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'tsla', 'atvi']
#availableStockList = ['ibm','aapl','msft','googl']

allData = pd.DataFrame([])
for stock in availableStockList:
    fullHolder = pd.DataFrame(quandl.get("WIKI/"+stock, trim_start = start, authtoken = token))
    closeHolder = pd.DataFrame(fullHolder['Adj. Close'])
    closeHolder.columns = [stock]
    if allData.empty:
        allData = closeHolder
    else:
        allData = allData.join(closeHolder, how='outer')
     
        
#Calculating the risk free rate
riskFreeData = pd.DataFrame(quandl.get("USTREASURY/BILLRATES", start_date="2017-01-11"))
FreeData = pd.DataFrame(riskFreeData["4 Wk Bank Discount Rate"])
tempReturns = FreeData.apply(lambda x: numpy.log(x) - numpy.log(x.shift(1)))
tempReturns = tempReturns.fillna(value = 0)
returns = tempReturns
riskFreeRate = numpy.mean(returns)[0]/30.5

        
# Defining the UI for each form #

Ui_MainWindow = uic.loadUiType("MainWindow.ui")[0]
Ui_StockChooser = uic.loadUiType("StockChooser.ui")[0]
Ui_StockPerformance = uic.loadUiType("StockPerformance.ui")[0]
Ui_StockAnalysis = uic.loadUiType("StockAnalysis.ui")[0]
Ui_Guide = uic.loadUiType("Guide.ui")[0]

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


class Portfolio:
    def __init__(self, stockList):
        try:
            self.stocks = stockList
            self.stockNames = chosenStockList
            self.weights = cv.matrix([1.0/len(self.stocks) for stock in self.stocks])
            my_stocks = pd.DataFrame([])
            for stock in self.stocks:
                tempDF = pd.DataFrame(self.stocks[stock].returns)
                if my_stocks.empty:
                    my_stocks = tempDF
                else:
                    my_stocks = my_stocks.join(tempDF, how='outer')
            self.returns = my_stocks.T
            self.covarianceMatrix = cv.matrix(numpy.cov(self.returns))
            self.average = cv.matrix(numpy.mean(self.returns, axis = 1))
            self.expectedReturn = blas.dot(self.average, self.weights)
            self.risk = numpy.sqrt(blas.dot(self.weights, self.covarianceMatrix * self.weights))
        except Exception as e:
            print(e)

    def calcReturn(self):
        self.expectedReturn = blas.dot(self.average, self.weights)

    def calcRisk(self):
        self.risk = numpy.sqrt(blas.dot(self.weights, self.covarianceMatrix * self.weights))
    
    def displayStocks(self):
        for x in range(len(self.stocks)):
            print('{0}: {1}'.format(self.stockNames[x], self.weights[x]))    
    

    def efficientFrontier(self):
        n = len(self.returns)
        returns = numpy.asmatrix(self.returns)
        N = 200
        mus = [10**(5.0 * t/N - 1.0) for t in range(N)]

        S = self.covarianceMatrix
        pbar = cv.matrix(numpy.mean(returns, axis = 1))


        G = -cv.matrix(numpy.eye(n))
        h = cv.matrix(0.0, (n,1))
        A = cv.matrix(1.0, (1,n))
        b = cv.matrix(1.0)

        portfolios = [cv.solvers.qp(mu*S, -pbar, G, h, A, b)['x'] for mu in mus]

        ## CALCULATE RISKS AND RETURNS FOR FRONTIER
        returns = [blas.dot(pbar, x) for x in portfolios]
        risks = [numpy.sqrt(blas.dot(x, S*x)) for x in portfolios] 
        
        return risks, returns
        


    def minVariance(self):
        n = len(self.returns)
        P = self.covarianceMatrix
        q = cv.matrix(0.0, (n,1))
        G = cv.matrix(-numpy.identity(n))
        h = cv.matrix(0.0,(n,1))
        A = cv.matrix(1.0,(1,n))
        b = cv.matrix(1.0)

        solution = cv.solvers.qp(P,q,G,h,A,b)['x']
        self.weights = solution
        
     
    def maxRet(self):
        n = len(self.returns)
        P = self.covarianceMatrix
        q = self.average        
        G = -cv.matrix(numpy.eye(n))
        h = cv.matrix(0.0, (n,1))
        A = cv.matrix(1.0, (1,n))
        b = cv.matrix(1.0)
        
        solution = cv.solvers.qp(P, -q, G, h, A, b)['x']
        self.weights = solution
    
    def givenRet(self, r_min):
        n = len(self.returns)        
        P = self.covarianceMatrix
        q = cv.matrix(numpy.zeros((n, 1)))  
        
        G = cv.matrix(numpy.concatenate((
		-numpy.transpose(numpy.array(self.average)), 
		-numpy.identity(n)), 0))    
        
        h = cv.matrix(numpy.concatenate((
		-numpy.ones((1,1))*r_min, 
		numpy.zeros((n,1))), 0))
        
        A = cv.matrix(1.0, (1,n))
        b = cv.matrix(1.0)
        
        solution = cv.solvers.qp(P, q, G, h, A, b)['x']
        self.weights = solution
        
    
    def personalPort(self, riskAv):
        n = len(self.returns)        
    
        N = 100
        mus = [10**(5.0 * t/N - 1.0) for t in range(N)]

        P = self.covarianceMatrix
        q = self.average        
        G = -cv.matrix(numpy.eye(n))
        h = cv.matrix(0.0, (n,1))
        A = cv.matrix(1.0, (1,n))
        b = cv.matrix(1.0)
        
        portfolios = [cv.solvers.qp(mu*P, -q, G, h, A, b)['x'] for mu in mus]
        
        tempReturns = [blas.dot(q, x) for x in portfolios]
        tempRisks = [numpy.sqrt(blas.dot(x, P*x)) for x in portfolios]
        
        utilitys = []
        
        for i, n in enumerate(tempReturns):            
            utilitys.append((tempReturns[i] - (0.5 * riskAv * tempRisks[i]**2)))
            
        maxIndex = utilitys.index(max(utilitys))
        solution = portfolios[maxIndex]
        self.weights = solution

 
# Main application window #

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)       
    
        self.ui.actionClose.triggered.connect(qApp.quit)
        self.ui.actionChoose_Stocks.triggered.connect(self.openStockChooser)
        self.ui.actionStock_Performance.triggered.connect(self.openStockPerformance)        
        self.ui.actionStock_Analysis.triggered.connect(self.openStockAnalysis)
        self.ui.actionGuide.triggered.connect(self.openHelpGuide)
        self.chosenStockNames = []
        self.chosenStockObjects = {}
        
        # Figure 5 - Efficient Frontier + Individual stocks
        self.figure5 = Figure(tight_layout = True)      
        self.canvas5 = FigureCanvas(self.figure5)
        self.toolbar5 = NavigationToolbar(self.canvas5 ,self)
        self.ui.graphLayout5.addWidget(self.canvas5, 1,0,1,2)
        self.ui.graphLayout5.addWidget(self.toolbar5, 0,0,1,2)        
        self.frontierGraph = self.figure5.add_subplot(111)         
        self.frontierGraph.set_xlabel("Risk (Standard Deviation) %")
        self.frontierGraph.set_ylabel("Expected Return %")
        
        # Figure 6 - Pie chart containing weights of portfolio
        self.figure6 = Figure(tight_layout = True)
        #self.figure6 = plt.figure()    
        self.canvas6 = FigureCanvas(self.figure6)
        self.ui.graphLayout6.addWidget(self.canvas6)
        self.weightChart = self.figure6.add_subplot(111)
            
     
    # Opening and closing each form.
    
    def openStockChooser(self):
        self.myStockChooser = StockChooser(self)
        self.myStockChooser.show()
    
    def openStockPerformance(self):
        self.myStockPerformance = StockPerformance()
        self.myStockPerformance.show()
    
    def openStockAnalysis(self):
        self.myStockAnalysis = StockAnalysis()
        self.myStockAnalysis.show()
        
    def openHelpGuide(self):
        self.myHelpGuide = HelpGuide()
        self.myHelpGuide.show()
        
    def createPortfolio(self):
        self.currentPortfolio = Portfolio(self.chosenStockObjects)
        self.statistics()
        self.plotFrontier()
        self.plotWeights()
        
    def enableOptimise(self):
        self.ui.minimalRisk.clicked.connect(self.minRiskOptimise)
        self.ui.maximumReturn.clicked.connect(self.maxRetOptimise)
        self.ui.specifiedRisk.clicked.connect(self.specRiskOptimise)
        
    
    def plotFrontier(self):
        self.figure5.clf()
        self.frontierGraph = self.figure5.add_subplot(111)         
        self.frontierGraph.set_xlabel("Daily Risk (Standard Deviation)")
        self.frontierGraph.set_ylabel("Daily Expected Return %")        
        x, y = self.currentPortfolio.efficientFrontier()
        self.frontierGraph.plot(x, y, "r-o", label="Efficient Frontier")
        for stock in self.chosenStockObjects:
            self.frontierGraph.plot(availableStockObjects[stock].SD, availableStockObjects[stock].average, "s" ,label=stock)
        self.frontierGraph.plot(self.currentPortfolio.risk, self.currentPortfolio.expectedReturn, "*", color="c",label="Portfolio")
        self.frontierGraph.legend()
        self.canvas5.draw()
     
    def statistics(self):
        self.currentPortfolio.calcReturn()
        self.currentPortfolio.calcRisk()
        tempRet = self.currentPortfolio.expectedReturn
        tempVar = self.currentPortfolio.risk
        ret = str(round(self.currentPortfolio.expectedReturn,6))
        var = str(round(self.currentPortfolio.risk,6))
        sharpe = str(round((tempRet - riskFreeRate)/tempVar, 6))
        self.ui.portfolioDetailsText.setText("Expected Return: " +ret+"%"+"\
        \nRisk: "+var+"%"+"\nSharpe Ratio: "+sharpe)     
        
    def plotWeights(self):
        self.figure6.clf()
        self.weightChart = self.figure6.add_subplot(111)
        weights = []
        labels = self.chosenStockNames
        for stock in self.currentPortfolio.weights:            
            weights.append(stock)       
        
        self.weightChart.pie(weights, labels = labels, autopct="%1.1f%%")
        self.weightChart.legend()
        self.canvas6.draw()
        
    def minRiskOptimise(self):        
        self.currentPortfolio.minVariance()                    
        self.statistics()
        self.plotFrontier()
        self.plotWeights()
        
    def maxRetOptimise(self):
        self.currentPortfolio.maxRet()
        self.statistics()
        self.plotFrontier()
        self.plotWeights()
        
    def specRiskOptimise(self):
        self.currentPortfolio.personalPort(self.ui.riskAversion.value())
        self.statistics()
        self.plotFrontier() 
        self.plotWeights()
    
# Stock Chooser Form #

class StockChooser(QWidget):
    def __init__(self, window):
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
        
        if len(chosenStockList) > 1:
            window.ui.portfolioStockList.clear()
            for stock in chosenStockList:
                item = QListWidgetItem()
                item.setText(stock)
                window.ui.portfolioStockList.addItem(item)
            window.chosenStockObjects = {name: Stock(name=name) for name in chosenStockList}
            window.chosenStockNames = chosenStockList
            window.createPortfolio()
            window.enableOptimise()
            self.close()
        
                         
 
# Stock Performance Form #

class StockPerformance(QWidget):
    def __init__(self):
        super(StockPerformance, self).__init__()
        self.ui = Ui_StockPerformance()
        self.ui.setupUi(self)
        
        # Figure 3 - All stock's price graph
        self.figure3 = Figure(tight_layout = True)      
        self.canvas3 = FigureCanvas(self.figure3)
        self.toolbar3 = NavigationToolbar(self.canvas3 ,self)
        self.ui.graphLayout3.addWidget(self.canvas3, 1,0,1,2)
        self.ui.graphLayout3.addWidget(self.toolbar3, 0,0,1,2)        
        self.allPriceGraph = self.figure3.add_subplot(111)         
        self.allPriceGraph.set_xlabel("Date/Time")
        self.allPriceGraph.set_ylabel("Stock Price")        
        for stock in availableStockList:
            self.allPriceGraph.plot(availableStockObjects[stock].Data, label=stock)
        self.allPriceGraph.legend()
        
        # Figure 4 - All stock's risk-return graph
        self.figure4 = Figure(tight_layout = True)      
        self.canvas4 = FigureCanvas(self.figure4)
        self.toolbar4 = NavigationToolbar(self.canvas4 ,self)
        self.ui.graphLayout4.addWidget(self.canvas4, 1,0,1,2)
        self.ui.graphLayout4.addWidget(self.toolbar4, 0,0,1,2)        
        self.riskReturnGraph = self.figure4.add_subplot(111)         
        self.riskReturnGraph.set_xlabel("Standard Deviation")
        self.riskReturnGraph.set_ylabel("Average Daily Return %")        
        for stock in availableStockList:
            self.riskReturnGraph.plot(availableStockObjects[stock].SD, availableStockObjects[stock].average, '*', label=stock)
        self.riskReturnGraph.legend()      
        
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
        
        # Tab Figures for graphs
        #Figure 1 - Stock Price Graph
        self.figure1 = Figure(tight_layout = True)      
        self.canvas1 = FigureCanvas(self.figure1)
        self.toolbar1 = NavigationToolbar(self.canvas1 ,self)
        self.ui.graphLayout1.addWidget(self.canvas1, 1,0,1,2)
        self.ui.graphLayout1.addWidget(self.toolbar1, 0,0,1,2)        
        self.priceGraph = self.figure1.add_subplot(111) 
        self.priceGraph.set_xlabel("Date/Time")
        self.priceGraph.set_ylabel("Stock Price")
       
        #Figure 2 - % Returns Graph
        self.figure2 = Figure(tight_layout = True)
        self.canvas2 = FigureCanvas(self.figure2)
        self.toolbar2 = NavigationToolbar(self.canvas2, self)
        self.ui.graphLayout2.addWidget(self.canvas2, 1,0,1,2)
        self.ui.graphLayout2.addWidget(self.toolbar2, 0,0,1,2)
        self.returnGraph = self.figure2.add_subplot(111)       
        
        
    def stockChose(self, item):
        #Setting analysis text        
        text = item.text()
        numRet = availableStockObjects[text].average[0]
        numStd = availableStockObjects[text].SD[0]
        ret = str(round(availableStockObjects[text].average[0],6))
        var = str(round(availableStockObjects[text].variance[0],6))
        std = str(round(availableStockObjects[text].SD[0],6))
        sharpe = str(round((numRet - riskFreeRate)/numStd,6))
        print(sharpe)
        self.ui.analysisText.setText("")
        self.ui.analysisText.setText("Average Return: " +ret+"%"+"\n\nVariance: "+var+"%"+"\n\nStandard Deviation: "+std\
                                     +"\n\nSharpe Ratio: " + sharpe)
        
        #Setting graph plots
        self.figure1.clf()
        self.figure2.clf()
        self.priceGraph = self.figure1.add_subplot(111)
        self.priceGraph.set_xlabel("Date/Time")
        self.priceGraph.set_ylabel("Adj. Close Price $")        
        self.returnGraph = self.figure2.add_subplot(111)
        self.returnGraph.set_xlabel("Date/Time")
        self.returnGraph.set_ylabel("Price Change %")        
        self.priceGraph.plot(availableStockObjects[text].Data)        
        self.returnGraph.plot(availableStockObjects[text].returns)
        self.canvas1.draw()
        self.canvas2.draw()
        
class HelpGuide(QWidget):
    def __init__(self):
        super(HelpGuide, self).__init__()
        self.ui = Ui_Guide()
        self.ui.setupUi(self)
        
        self.ui.guideText.setText("Before creating a portfolio, you can check the\
        performance and statistics of the available stocks by going to Menu -> Stocks.\
        \n\nTo create a portfolio, first choose the stocks that you would like to\
        include using the Menu: Portfolio -> Choose Stocks.")
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())