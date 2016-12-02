import matplotlib
import scipy
import numpy
import sklearn
import quandl
import pandas as pd
import os
import time
from sqlalchemy import create_engine
import mysql.connector
from datetime import datetime

quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"

token = 'p_qounXgMs57T9nYAurW'
start = '2016-01-01'
stocklist = ['l_ibm','aapl','msft','googl']
engine = create_engine('mysql+mysqlconnector://root:machinelearning1@localhost:3306/stockdata')
dbschema = 'stockdata'

for stock in stocklist:
    df = quandl.get("YAHOO/"+ stock,trim_start = start, authtoken=token)
    print(stock)
    print(df)
    df.to_sql(stock, con = engine, schema = dbschema, if_exists = 'append',index=True)

#df = quandl.get("YAHOO/l_ibm",trim_start = start, authtoken=token)
#print(df)
#df.to_sql('l_ibm', con = engine, schema = dbschema, if_exists = 'append',index=True)
