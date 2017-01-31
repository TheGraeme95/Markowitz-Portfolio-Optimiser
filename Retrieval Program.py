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
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler


quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"

token = 'p_qounXgMs57T9nYAurW'
start = '2010-01-01'

dbschema = 'Stockdata'
daily = date.today()
end = daily.replace(day=daily.day-1)
daily = daily.replace(day=daily.day)

stocklist = ['ibm','aapl','msft','googl']
engine = create_engine('mysql+mysqlconnector://TheGraeme95:machinelearning1@stockdatadb.czl4fjyxavu7.eu-west-1.rds.amazonaws.com:3306/Stockdata')

print(daily)

## Get all stocks from start date

def getAllStocks():
    try:
        for stock in stocklist:
            df = quandl.get("YAHOO/"+ stock, trim_start = start, trim_end = end, authtoken = token)
            df['Name'] = stock
            print(stock)
            print(df)
            df.to_sql(stock, con = engine, schema = dbschema, if_exists = 'replace', index = True)
    except Exception as e:
        print("failed getting bulk stock data because",str(e))

## Get daily stock updates
      
def getDailyStocks():
    try:
        for stock in stocklist:
            df = quandl.get("YAHOO/"+ stock, trim_start = daily, authtoken = token)
            df['Name'] = stock
            print(stock)
            df.to_sql(stock, con = engine, schema = dbschema, if_exists = 'append', index = True)
    except Exception as error:
        print("failed getting daily stock data beacuse",str(error))


scheduler = BlockingScheduler()
scheduler.add_job(getDailyStocks, 'cron', hour = 23)
scheduler.start()
#getAllStocks()



#scheduler = Blocking

