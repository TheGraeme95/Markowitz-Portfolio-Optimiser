import matplotlib
import scipy
import numpy
import sklearn
import quandl
import pandas as pd
import os
import time
from datetime import datetime
quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"

token = 'p_qounXgMs57T9nYAurW'
start = '2016-01-01'
stocklist = ['L_IBM','AAPL','MSFT','GOOGL','DELL','','','','','','','','','','']


df = quandl.get("YAHOO/L_IBM",trim_start = start, authtoken=token)
print(df)
