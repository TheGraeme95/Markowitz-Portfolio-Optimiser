import quandl
import pandas as pd
from sqlalchemy import create_engine
import mysql.connector ##conda install mysql-connector-python / pip install mysql-python
from datetime import date



quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"

token = 'p_qounXgMs57T9nYAurW'
start = '2016-01-01'

dbschema = 'Stockdata'
daily = date.today()
end = daily.replace(day=daily.day)
daily = daily.replace(day=daily.day)

stocklist = ['ibm','aapl','msft','googl']#, 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'tsla', 'atvi']
#engine = create_engine('mysql+mysqlconnector://TheGraeme95:machinelearning1@stockdatadb.czl4fjyxavu7.eu-west-1.rds.amazonaws.com:3306/Stockdata')
engine = create_engine('mysql+mysqlconnector://root:machinelearning1@localhost:3306/Stockdata')
## Get all stocks from start date


allData = pd.DataFrame([])
for stock in stocklist:
    fullHolder = pd.DataFrame(quandl.get("WIKI/"+stock, trim_start = start, authtoken = token))
    closeHolder = pd.DataFrame(fullHolder['Adj. Close'])
    closeHolder.columns = [stock]
    if allData.empty:
        allData = closeHolder
    else:
        allData = allData.join(closeHolder, how='outer')


#allData.to_sql("aapl", con = engine, schema = "stockdata", if_exists = 'replace', index=True)


print("done")




#def getAllStocks():
#    try:
#        for stock in stocklist:
#            df = quandl.get("WIKI/"+ stock, trim_start = start, trim_end = end, authtoken = token)
#            df['Name'] = stock            
#            df.to_sql(stock, con = engine, schema = dbschema, if_exists = 'replace', index = True)
#        print("All stock data since ",str(start), " successfully retrieved.")
#    except Exception as e:
#        print("failed getting bulk stock data because",str(e))


#getAllStocks()