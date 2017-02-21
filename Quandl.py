import numpy
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import quandl
import cvxopt as cv


stockList = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'tsla', 'atvi']
dbSchema = 'Stockdata'

quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"
token = 'p_qounXgMs57T9nYAurW'
start = '2014-01-01'

class Stock:
    def __init__(self,name):
        try:
            self.name = name
            self.Data = quandl.get("WIKI/"+ name, trim_start = start, authtoken = token)
            tempReturns = pd.DataFrame(numpy.log(1 + self.Data['Adj. Close'].tail(252*3).pct_change(1)))
            tempReturns = tempReturns.rename(columns = {'Adj. Close' : self.name})
            self.returns = tempReturns.fillna(value = 0)
            #self.returns.loc[:,] *= 100
            self.average = numpy.mean(self.returns)
            self.variance = numpy.var(self.returns)
            self.SD = numpy.std(self.returns)            
        except Exception as e:
            print("Not a an available stock from the list.", str(e))
            
    def displayStats(self):
        try:
            print(self.name,"using data for 1 year:")
            print("Average Daily Return:", self.average,"%")
            print("Standard Deviation:", self.SD,"%")
            print("Variance:",self.variance,"%")
        except Exception as e:
            print(e)
            
def plotStocks():
    try:
        my_stocks = pd.DataFrame([])
        for ticker in stockList:
            tempDF = pd.DataFrame({ticker:Stock(ticker).Data['Adj. Close'].tail(252*3)})
            my_stocks = pd.concat([my_stocks,tempDF], axis = 1)
        print(my_stocks)
        my_stocks.plot(grid = True)
    except Exception as e:
        print(e)

def plotReturns():
    try:
        my_stocks = pd.DataFrame([])
        for ticker in stockList:
            tempDF = pd.DataFrame(Stock(ticker).returns)            
            my_stocks = pd.concat([my_stocks, tempDF],axis = 1)
        print(my_stocks)
        my_stocks.plot(grid = True)        
    except Exception as e:
        print(e)

def plotMeanVar():
    try:
        x = []
        y = []
        fig, ax = plt.subplots()
        for ticker in stockList:
            temp = Stock(ticker)
            x.append(temp.SD)
            y.append(temp.average)
        ax.scatter(x,y)
        
        for i, txt in enumerate(stockList):
            ax.annotate(txt, (x[i],y[i]))
    except Exception as e:
        print(e)

            

def covarianceMatrix():
    try:
        my_stocks = pd.DataFrame([])
        for ticker in stockList:
            tempDF = pd.DataFrame(Stock(ticker).returns)                    
            my_stocks = pd.concat([my_stocks,tempDF], axis = 1)
            my_stocks = my_stocks.fillna(value = 0)                                                             
        covMatrix = numpy.cov(my_stocks, rowvar = False)               
        #plt.imshow(covMatrix)
        #plt.show()
        return covMatrix
    except Exception as e:
        print(e)
        
def meanReturns():
    try:
        mean_returns = pd.DataFrame([])
        for ticker in stockList:
            ticker = Stock(ticker)
            mean_returns = pd.concat([mean_returns, ticker.average])        
        return mean_returns        
    except Exception as e:
        print(e)
        

        
testMatrix = numpy.asarray(meanReturns()[0])

def portfolioOpt1():
    r_min = 0.005
    covM = cv.matrix(covarianceMatrix())
    meanR = cv.matrix(testMatrix)
    n = int(len(stockList))
    P = covM
    q = cv.matrix(numpy.zeros(shape = (n,1)))
    
    G = cv.matrix(numpy.concatenate((
                 -numpy.transpose(numpy.array(meanR)), 
                 -numpy.identity(n)), 0))
    
    h = cv.matrix(numpy.concatenate((
                 -numpy.ones((1,1))*r_min, 
                  numpy.zeros((n,1))), 0))
    
    A = cv.matrix(1.0, (1,n))
    b = cv.matrix(1.0)
    
    sol = cv.solvers.qp(P, q, G, h, A, b)
    print(sol['x'])

def portfolioOpt2():
    r_min = 0.005
    covM = cv.matrix(covarianceMatrix())
    meanR = cv.matrix(testMatrix)
    n = int(len(stockList))
    P = covM
    q = cv.matrix(numpy.zeros(shape = (n,1)))
    
    G = cv.matrix(numpy.concatenate((
                 -numpy.transpose(numpy.array(meanR)), 
                 -numpy.identity(n)), 0))
    
    h = cv.matrix(numpy.concatenate((
                 -numpy.ones((1,1))*r_min, 
                  numpy.zeros((n,1))), 0))
    
    A = cv.matrix(1.0, (1,n))
    b = cv.matrix(1.0)
    
    sol = cv.solvers.qp(P, q, G, h, A, b)
    print(sol['x'])






def portfolioOpt3():
    n = int(len(stockList))
    covM = covarianceMatrix()
    S = cv.matrix(covM)
    pbar = cv.matrix(testMatrix)
    
    G  = -cv.matrix(numpy.eye(n))
    h = cv.matrix(0.0, (n, 1))
    
    ## Ax = b constraint for weighting sum = 1 Lagrange multiplier
    A = cv.matrix(1.0, (1, n))
    b = cv.matrix(1.0)
    
    solution = numpy.array(cv.solvers.qp(S, -pbar, G, h, A, b)['x'])
    print(solution)
    portfolioReturn = testMatrix.T * solution
    print('Portfolio Return:', portfolioReturn.sum(),'%')
    portfolioVariance = numpy.sum((numpy.dot(solution.T, covM) * solution), dtype = float)
    print('Portfolio Variance:', portfolioVariance,'%')
    #return solution, portfolioReturn, portfolioVariance

#print(meanReturns())
#portfolioOpt3()
plotMeanVar()

#https://datanitro.com/blog/mean-variance-optimization
#http://nbviewer.jupyter.org/github/cvxgrp/cvx_short_course/blob/master/applications/portfolio_optimization.ipynb