import numpy
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://TheGraeme95:machinelearning1@stockdatadb.czl4fjyxavu7.eu-west-1.rds.amazonaws.com:3306/Stockdata')

stockList = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'lnkd', 'tsla', 'atvi']
dbSchema = 'Stockdata'

class Stock:
    def __init__(self,name):
        try:
            self.name = name
            self.Data = pd.read_sql_table(name, con = engine, schema = dbSchema, index_col = 'Date')
        except Exception as e:
            print("Not a an available stock from the list.", str(e))
            
    def dailyReturns(self, years):
        try:
            self.returns = self.Data['Adj. Close'].tail(252*years).pct_change(1)
            returns.loc[:,] *= 100
            return returns
        except Exception as e:
            print(e)

    def averageReturn()
            
print("List of available stocks:\n",stockList)
chosenStock = Stock(input("Which stock would you like to look at?\n"))
print(chosenStock.dailyReturns(1))
