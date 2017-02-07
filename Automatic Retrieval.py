import quandl
from sqlalchemy import create_engine
from datetime import date
#from apscheduler.schedulers.blocking import BlockingScheduler

quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"

token = 'p_qounXgMs57T9nYAurW'
start = '2010-01-01'

dbschema = 'Stockdata'
daily = date.today()
yesterday = daily.replace(day=daily.day)

stocklist = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'lnkd', 'tsla', 'atvi']
engine = create_engine('mysql+mysqlconnector://TheGraeme95:machinelearning1@stockdatadb.czl4fjyxavu7.eu-west-1.rds.amazonaws.com:3306/Stockdata')

def getDailyStocks():
    try:
        for stock in stocklist:
            df = quandl.get("WIKI/"+ stock, trim_start = yesterday, authtoken = token)
            df['Name'] = stock
            print(stock)
            df.to_sql(stock, con = engine, schema = dbschema, if_exists = 'append', index = True)
        print("All stocks retrieved successfully")
    except Exception as error:
        print("failed getting daily stock data beacuse",str(error))
        
#scheduler = BlockingScheduler()
#scheduler.add_job(getDailyStocks, 'cron', hour = 23)
#scheduler.start()
getDailyStocks()

