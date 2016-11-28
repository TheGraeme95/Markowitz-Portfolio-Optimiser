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
stocklist = ['L_IBM','AAPL','MSFT','GOOGL','DELL','','','','','','','','','','']
#cnx = mysql.connector.connect(user='root', password='machinelearning1', host='localhost', database='stockdata')
engine = create_engine('mysql+mysqlconnector://root:machinelearning1@localhost:3306/stockdata')
dbschema = 'stockdata'


df = quandl.get("YAHOO/L_IBM",trim_start = start, authtoken=token)
print(df)
df.to_sql('l_ibm', con = engine, schema = dbschema, if_exists = 'append',index=True)
