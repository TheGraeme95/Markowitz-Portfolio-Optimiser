import numpy
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://TheGraeme95:machinelearning1@stockdatadb.czl4fjyxavu7.eu-west-1.rds.amazonaws.com:3306/Stockdata')

stocklist = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'lnkd', 'tsla', 'atvi']
dbSchema = 'Stockdata'

class Stock:
    def __init__(self,name):
        try:
            self.name = name
            self.Data = pd.read_sql_table(name, con = engine, schema = dbSchema, index_col = 'Date')                       
        except Exception as e:
            print("Not a valid stock name in the WIKI dataset.", str(e))
            
def calculateReturn(Stock):
    try:
        returns = Stock.Data['Adj. Close'].tail(252*5).pct_change(1)
        print(returns)
        historicalReturn = ((1/(252*5))*(returns.sum(axis = 0)))
        print("The historical return for the last 5 years",Stock.name,"is",historicalReturn,"%")
    except Exception as e:
        print(e)
            
#IBM = Stock('ibm')
#IBMprices = IBM.close.pct_change(1)
#print(IBMprices)
#(IBM.Data['Adj. Close'].pct_change(1))

input1 = input("Which stock would you like to look at?\n")
print("Loading",input1, "data..\n")
chosenStock = Stock(input1)
calculateReturn(chosenStock)



