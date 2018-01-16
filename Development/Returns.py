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
            print("Not a an available stock from the list.", str(e))
            
def calculateStats(Stock):
    try:
        stockYears = int(input("How many years of data would you like to use? (1-5)\n"))
        returns = Stock.Data['Adj. Close'].tail(252*stockYears).pct_change(1)
        returns.loc[:,] *= 100
        print(returns,"\n")
        averageReturn = numpy.mean(returns)
        stockVariance = numpy.var(returns)
        stockSD = numpy.std(returns)
        print(Stock.name,"using last",stockYears,"years of data:")
        print("Average Daily Return:",averageReturn,"%")
        print("Standard Deviation:", stockSD)
        print("Variance:",stockVariance,"%")
        plt.plot(returns)
    except Exception as e:
        print(e)
            
#def calculateCovariance(Stock, Stock):
#    try:
#                                
#    except Exception as e:
#        print(e)

        
input1 = input("Which stock would you like to look at?\n")
print("Loading",input1, "data..\n")
chosenStock = Stock(input1)
calculateStats(chosenStock)



