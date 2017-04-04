import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, qApp, QWidget, QListWidget, QListWidgetItem
from PyQt5 import uic, QtCore, QtGui
 

availableStockList = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'tsla', 'atvi']

Ui_MainWindow = uic.loadUiType("MainWindow.ui")[0]
Ui_StockChooser = uic.loadUiType("StockChooser.ui")[0]
Ui_StockPerformance = uic.loadUiType("StockPerformance.ui")[0]
Ui_StockAnalysis = uic.loadUiType("StockAnalysis.ui")[0]
 
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
    
 

class StockChooser(QWidget):
    def __init__(self):
        super(StockChooser, self).__init__()
        self.ui = Ui_StockChooser()
        self.ui.setupUi(self)
        for stock in availableStockList:
            item = QListWidgetItem()
            item.setText(stock)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.ui.choiceList.addItem(item)
            
            
        
    

class StockPerformance(QWidget):
    def __init__(self):
        super(StockPerformance, self).__init__()
        self.ui = Ui_StockPerformance()
        self.ui.setupUi(self)
        
class StockAnalysis(QWidget):
    def __init__(self):
        super(StockAnalysis, self).__init__()
        self.ui = Ui_StockAnalysis()
        self.ui.setupUi(self)
        

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())