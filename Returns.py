import numpy
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://TheGraeme95:machinelearning1@stockdatadb.czl4fjyxavu7.eu-west-1.rds.amazonaws.com:3306/Stockdata')

stocklist = ['ibm','aapl','msft','googl']
dbSchema = 'Stockdata'

class Stock:
    def __init__(self,name):
        try:
            self.name = name
            self.Data = pd.read_sql_table(name, con = engine, schema = dbSchema, index_col = 'Date')                       
        except Exception as e:
            print("Not a valid stock name in the WIKI dataset.", str(e))
            
            
#IBM = Stock('ibm')
#IBMprices = IBM.close.pct_change(1)
#print(IBMprices)
IBM = Stock('ibm')
print(IBM.Data['Adj. Close'].pct_change(1))