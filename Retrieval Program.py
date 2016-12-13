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
import Schedule

quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"

token = 'p_qounXgMs57T9nYAurW'
start = '2016-01-01'
stocklist = ['ibm','aapl','msft','googl']
engine = create_engine('mysql+mysqlconnector://TheGraeme95:machinelearning1@stockdatadb.czl4fjyxavu7.eu-west-1.rds.amazonaws.com:3306/Stockdata')
dbschema = 'Stockdata'

def GetStocks():
    for stock in stocklist:
        df = quandl.get("YAHOO/"+ stock,trim_start = start, authtoken=token)
        df['Name']=stock
        print(stock)
        print(df)
        df.to_sql(stock, con = engine, schema = dbschema, if_exists = 'replace',index=True)

schedule.every().day.at("04:30").do(GetStocks)

while True:
    schedule.run_pending()
    time.sleep(60)


#df = quandl.get("YAHOO/l_ibm",trim_start = start, authtoken=token)
#print(df)
#df.to_sql('l_ibm', con = engine, schema = dbschema, if_exists = 'append',index=True)
