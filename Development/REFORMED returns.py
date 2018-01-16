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
    def __init__(self,name):
        try:
            self.name = name
            self.Data = pd.read_sql_table(name, con = engine, schema = dbSchema, index_col = 'Date')
            tempReturns = pd.DataFrame(numpy.log(1 + self.Data['Adj. Close'].tail(252*1).pct_change(1)))
            self.returns = tempReturns.rename(columns = {'Adj. Close' : self.name})
            #self.returns.loc[:,] *= 100
            self.average = numpy.mean(self.returns)
            self.variance = numpy.var(self.returns)
            self.SD = numpy.std(self.returns)            
        except Exception as e:
            print("Not a an available stock from the list.", str(e))


def covarianceMatrix():
    try:
        my_stocks = pd.DataFrame([])
        for ticker in stockList:
            ticker = Stock(ticker)                      
            my_stocks = pd.concat([my_stocks,ticker.returns], axis = 1)
            print(ticker.returns)
            #my_stocks = my_stocks.join(ticker.returns, how = 'outer')                                        
        covMatrix = numpy.cov(my_stocks, rowvar = False, bias = 1)
        print(my_stocks)
    except Exception as e:
        print(e)

covarianceMatrix()

        

        
