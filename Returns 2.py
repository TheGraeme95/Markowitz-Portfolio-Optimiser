import numpy
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://TheGraeme95:machinelearning1@stockdatadb.czl4fjyxavu7.eu-west-1.rds.amazonaws.com:3306/Stockdata')

stockList = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'tsla', 'atvi']
dbSchema = 'Stockdata'

class Stock:
    def __init__(self, name):
        try:
            self.name = name
            self.Data = pd.read_sql_table(name, con = engine, schema = dbSchema, index_col = 'Date')
        except Exception as e:
            print("Not a an available stock from the list.", str(e))
            
    def dailyReturns(self, years):
        try:
            self.years = years
            self.returns = numpy.log(1 + self.Data['Adj. Close'].tail(252*self.years).pct_change(1))       
            #self.returns.loc[:,] *= 100
            self.average = numpy.mean(self.returns)
            self.variance = numpy.var(self.returns)
            self.SD = numpy.std(self.returns)
            return self.returns
        except Exception as e:
            print(e)
            
    def displayStats(self):
        try:
            print(self.name,"using the last",self.years,"years of data:")
            print("Average Daily Return:", self.average,"%")
            print("Standard Deviation:", self.SD,"%")
            print("Variance:",self.variance,"%")
        except Exception as e:
            print(e)
            
def covarianceMatrix():
    try:
        my_stocks = []
        for ticker in stockList:            
            my_stocks.append(Stock(ticker))            
        print(Stock.name for Stock in my_stocks)
    except Exception as e:
        print(e)
            
print("List of available stocks:\n",stockList)
chosenStock = Stock(input("Which stock would you like to look at?\n"))
chosenYears = int(input("How many years of data?\n"))
print(chosenStock.dailyReturns(chosenYears))
chosenStock.displayStats()
#covarianceMatrix()