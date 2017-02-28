import numpy
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import quandl
import cvxopt as cv
from cvxopt import blas

#tempStockList = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'tsla', 'atvi']
tempStockList = ['ibm','aapl','msft','googl']

dbSchema = 'Stockdata'
quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"
token = 'p_qounXgMs57T9nYAurW'
start = '2015-01-01'

class Stock:
    def __init__(self,name):
        try:
            self.name = name            
            self.Data = quandl.get("WIKI/"+ name, trim_start = start, authtoken = token)
            tempAdj = pd.DataFrame(self.Data['Adj. Close'])
            tempReturns = tempAdj.apply(lambda x: numpy.log(x) - numpy.log(x.shift(1)))
            tempReturns = tempReturns.rename(columns = {'Adj. Close' : self.name})
            tempReturns = tempReturns.fillna(value = 0)
            self.returns = tempReturns
            self.average = numpy.mean(self.returns)
            self.variance = numpy.var(self.returns)
            self.SD = numpy.std(self.returns)            
        except Exception as e:
            print(e)
            
    def displayStats(self):
        try:
            print(self.name,"using data for 1 year:")
            print("Average Daily Return:", self.average,"%")
            print("Standard Deviation:", self.SD,"%")
            print("Variance:",self.variance,"%")
        except Exception as e:
            print(e)
 
stockList = {name: Stock(name=name) for name in tempStockList}
           
def plotStocks():
    try:
        my_stocks = pd.DataFrame([])
        for ticker in tempStockList:
            tempDF = pd.DataFrame({ticker:stockList[ticker].Data['Adj. Close']})
            my_stocks = pd.concat([my_stocks,tempDF], axis = 1)
        print(my_stocks)
        my_stocks.plot(grid = True)
    except Exception as e:
        print(e)

def plotReturns():
    try:
        my_stocks = pd.DataFrame([])
        for ticker in tempStockList:
            tempDF = pd.DataFrame(stockList[ticker].returns)
            if my_stocks.empty:
                my_stocks = tempDF
            else:
                my_stocks = my_stocks.join(tempDF, how='outer')            
            #print(tempDF)
            #my_stocks = pd.concat([my_stocks, tempDF],axis = 1)
        print(my_stocks)
        my_stocks.plot(grid = True)        
    except Exception as e:
        print(e)

def plotMeanVar():
    try:
        x = []
        y = []
        fig, ax = plt.subplots()
        for ticker in tempStockList:            
            x.append(stockList[ticker].SD)
            y.append(stockList[ticker].average)
        ax.scatter(x,y)
        
        for i, txt in enumerate(tempStockList):
            ax.annotate(txt, (x[i],y[i]))
    except Exception as e:
        print(e)

            
def covarianceMatrix():
    try:
        my_stocks = pd.DataFrame([])
        for ticker in tempStockList:
            tempDF = pd.DataFrame(stockList[ticker].returns)                    
            my_stocks = pd.concat([my_stocks,tempDF], axis = 1)
            my_stocks = my_stocks.fillna(value = 0)                                                             
        covMatrix = numpy.cov(my_stocks.T)               
        #plt.imshow(covMatrix)
        #plt.show()
        return covMatrix
    except Exception as e:
        print(e)
        
def meanReturns():
    try:
        mean_returns = pd.DataFrame([])
        for ticker in tempStockList:            
            mean_returns = pd.concat([mean_returns, stockList[ticker].average])        
        return mean_returns        
    except Exception as e:
        print(e)
        
def random_weights(n):
    k = numpy.random.rand(n)
    return k / sum(k)


def random_portfolio(returns):
    p = numpy.asmatrix(meansMatrix)
    w = numpy.asmatrix(random_weights(returns.shape[0]))
    C = numpy.asmatrix(CovMatrix)
    
    mu = w * p.T
    sigma = numpy.sqrt(w * C * w.T)
    
    if sigma > 2:
        return random_portfolio(returns)
    return mu, sigma


def plotRandomPortfolios(n):
    n_portfolios = n
    print('Generating',n_portfolios,'random portfolios')
    means, stds = numpy.column_stack([
        random_portfolio(meansMatrix) 
        for _ in range(n_portfolios)])
    
    plt.plot(stds, means, 'o', markersize=5)
    plt.xlabel('std')
    plt.ylabel('mean')
    plt.title('Mean and standard deviation of returns of randomly generated portfolios')

def convert_portfolios(portfolios):
    ''' Takes in a cvxopt matrix of portfolios, returns a list of portfolios '''
    port_list = []
    for portfolio in portfolios:
        temp = numpy.array(portfolio).T
        port_list.append(temp[0].tolist())
        
    return port_list

def efficientFrontier(inputReturns):
    n = len(inputReturns)
    returns = numpy.asmatrix(inputReturns)
    
    print("\n RETURNS",returns)
    print("\n N",n)

    N = 100
    mus = [10**(5.0 * t/N - 1.0) for t in range(N)]
    
    S = cv.matrix(numpy.cov(returns))
    pbar = cv.matrix(numpy.mean(returns, axis = 1))
    
        
    G = -cv.matrix(numpy.eye(n))
    h = cv.matrix(0.0, (n,1))
    A = cv.matrix(1.0, (1,n))
    b = cv.matrix(1.0)
    
    portfolios = [cv.solvers.qp(mu*S, -pbar, G, h, A, b)['x'] for mu in mus]
    
    port_list = convert_portfolios(portfolios)
    
    
    ## CALCULATE RISKS AND RETURNS FOR FRONTIER
    returns = [blas.dot(pbar, x) for x in portfolios]    
    risks = [numpy.sqrt(blas.dot(x, S*x)) for x in portfolios] #np.sqrt returns the stdev, not variance
   
    ## CALCULATE THE 2ND DEGREE POLYNOMIAL OF THE FRONTIER CURVE
    m1 = numpy.polyfit(returns, risks, 2)    
    x1 = (numpy.sqrt(m1[2] / m1[0]))    
    # CALCULATE THE OPTIMAL PORTFOLIO
    wt = cv.solvers.qp(cv.matrix(x1 * S), -pbar, G, h, A, b)['x'] #Is this the tangency portfolio? X1 = slope from origin?  

    return numpy.asarray(wt), returns, risks, port_list


stockList = {name: Stock(name=name) for name in tempStockList}

CovMatrix = covarianceMatrix()
meansMatrix = numpy.asarray(meanReturns()[0])



my_stocks = pd.DataFrame([])
for ticker in tempStockList:
    tempDF = pd.DataFrame(stockList[ticker].returns)
    if my_stocks.empty:
        my_stocks = tempDF
    else:
        my_stocks = my_stocks.join(tempDF, how='outer')
            
my_stocks = my_stocks.T
plotRandomPortfolios(20000)

weights, returns, risks, portlist = efficientFrontier(my_stocks)
plt.ylabel('mean')
plt.xlabel('std')
plt.plot(risks, returns, 'r-o')

minIndex = risks.index(min(risks))
plt.plot(risks[minIndex],returns[minIndex], 'o')
#https://datanitro.com/blog/mean-variance-optimization
#http://nbviewer.jupyter.org/github/cvxgrp/cvx_short_course/blob/master/applications/portfolio_optimization.ipynb