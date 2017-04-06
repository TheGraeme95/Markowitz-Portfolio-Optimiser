import numpy
import pandas as pd
import quandl
#import matplotlib as plt
from matplotlib import pyplot as plt
import cvxopt as cv
from cvxopt import blas

cv.solvers.options['show_progress'] = False
dbSchema = 'Stockdata'
quandl.ApiConfig.api_key = "p_qounXgMs57T9nYAurW"
token = 'p_qounXgMs57T9nYAurW'
start = '2015-01-01'

availableStockList = ['ibm','aapl','msft','googl', 'fb', 'yhoo', 'csco', 'intc', 'amzn', 'ebay', 'orcl', 'nflx', 'tsla', 'atvi']
tempAvailableStockList = ['ibm', 'aapl', 'msft', 'googl']

allData = pd.DataFrame([])
for stock in tempAvailableStockList:
    fullHolder = pd.DataFrame(quandl.get("WIKI/"+stock, trim_start = start, authtoken = token))
    closeHolder = pd.DataFrame(fullHolder['Adj. Close'])
    closeHolder.columns = [stock]
    if allData.empty:
        allData = closeHolder
    else:
        allData = allData.join(closeHolder, how='outer')

class Stock:
    def __init__(self,name):
        try:
            self.name = name
            self.Data = pd.DataFrame(allData[name])
            tempAdj = self.Data
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

chosenStockList = ['ibm','aapl','msft','googl']
chosenStocks = {name: Stock(name=name) for name in chosenStockList}

class Portfolio:
    def __init__(self, stockList):
        try:
            self.stocks = stockList
            self.stockNames = chosenStockList
            self.weights = cv.matrix([1.0/len(self.stocks) for stock in self.stocks])
            my_stocks = pd.DataFrame([])
            for stock in self.stocks:
                tempDF = pd.DataFrame(self.stocks[stock].returns)
                if my_stocks.empty:
                    my_stocks = tempDF
                else:
                    my_stocks = my_stocks.join(tempDF, how='outer')
            self.returns = my_stocks.T
            self.covarianceMatrix = cv.matrix(numpy.cov(self.returns))
            self.average = cv.matrix(numpy.mean(self.returns, axis = 1))
            self.expectedReturn = blas.dot(self.average, self.weights)
            self.risk = numpy.sqrt(blas.dot(self.weights, self.covarianceMatrix * self.weights))
        except Exception as e:
            print(e)

    def calcReturn(self):
        self.expectedReturn = blas.dot(self.average, self.weights)

    def calcRisk(self):
        self.risk = numpy.sqrt(blas.dot(self.weights, self.covarianceMatrix * self.weights))
    
    def displayStocks(self):
        for x in range(len(self.stocks)):
            print('{0}: {1}'.format(self.stockNames[x], self.weights[x]))
    
    def portPlot(self):
        plt.ylabel('mean')
        plt.xlabel('std')
        plt.plot(self.risk, self.expectedReturn, 'r-o')

    def efficientFrontier(self):
        n = len(self.returns)
        returns = numpy.asmatrix(self.returns)
        N = 100
        mus = [10**(5.0 * t/N - 1.0) for t in range(N)]

        S = self.covarianceMatrix
        pbar = cv.matrix(numpy.mean(returns, axis = 1))


        G = -cv.matrix(numpy.eye(n))
        h = cv.matrix(0.0, (n,1))
        A = cv.matrix(1.0, (1,n))
        b = cv.matrix(1.0)

        portfolios = [cv.solvers.qp(mu*S, -pbar, G, h, A, b)['x'] for mu in mus]

        ## CALCULATE RISKS AND RETURNS FOR FRONTIER
        returns = [blas.dot(pbar, x) for x in portfolios]
        risks = [numpy.sqrt(blas.dot(x, S*x)) for x in portfolios] #np.sqrt returns the stdev, not variance

        ## CALCULATE THE 2ND DEGREE POLYNOMIAL OF THE FRONTIER CURVE
        m1 = numpy.polyfit(returns, risks, 2)
        x1 = (numpy.sqrt(m1[2] / m1[0]))
        # CALCULATE THE OPTIMAL PORTFOLIO
        wt = cv.solvers.qp(cv.matrix(x1 * S), -pbar, G, h, A, b)['x'] #Is this the tangency portfolio? X1 = slope from origin?

        plt.ylabel('mean')
        plt.xlabel('std')
        plt.plot(risks, returns, 'r-o')

    def minVariance(self):
        n = len(self.returns)
        P = self.covarianceMatrix
        q = cv.matrix(0.0, (n,1))
        G = cv.matrix(-numpy.identity(n))
        h = cv.matrix(0.0,(n,1))
        A = cv.matrix(1.0,(1,n))
        b = cv.matrix(1.0)

        solution = cv.solvers.qp(P,q,G,h,A,b)['x']
        self.weights = solution
        
     
    def maxRet(self):
        n = len(self.returns)
        P = self.covarianceMatrix
        q = self.average        
        G = -cv.matrix(numpy.eye(n))
        h = cv.matrix(0.0, (n,1))
        A = cv.matrix(1.0, (1,n))
        b = cv.matrix(1.0)
        
        solution = cv.solvers.qp(P, -q, G, h, A, b)['x']
        self.weights = solution
    
    def givenRet(self, r_min):
        n = len(self.returns)        
        P = self.covarianceMatrix
        q = cv.matrix(numpy.zeros((n, 1)))  
        
        G = cv.matrix(numpy.concatenate((
		-numpy.transpose(numpy.array(self.average)), 
		-numpy.identity(n)), 0))    
        
        h = cv.matrix(numpy.concatenate((
		-numpy.ones((1,1))*r_min, 
		numpy.zeros((n,1))), 0))
        
        A = cv.matrix(1.0, (1,n))
        b = cv.matrix(1.0)
        
        solution = cv.solvers.qp(P, q, G, h, A, b)['x']
        self.weights = solution
        
    
    def personalPort(self, riskAv):
        n = len(self.returns)        
    
        N = 100
        mus = [10**(5.0 * t/N - 1.0) for t in range(N)]

        P = self.covarianceMatrix
        q = self.average        
        G = -cv.matrix(numpy.eye(n))
        h = cv.matrix(0.0, (n,1))
        A = cv.matrix(1.0, (1,n))
        b = cv.matrix(1.0)
        
        portfolios = [cv.solvers.qp(mu*P, -q, G, h, A, b)['x'] for mu in mus]
        
        tempReturns = [blas.dot(q, x) for x in portfolios]
        tempRisks = [numpy.sqrt(blas.dot(x, P*x)) for x in portfolios]
        
        utilitys = []
        
        for i, n in enumerate(tempReturns):            
            utilitys.append((tempReturns[i] - (0.5 * riskAv * tempRisks[i]**2)))
            
        maxIndex = utilitys.index(max(utilitys))
        solution = portfolios[maxIndex]
        self.weights = solution
              
    
    
    
    
def random_weights(n):
    k = numpy.random.rand(n)
    return k / sum(k)

def random_portfolio(portfolio):
    p = numpy.asmatrix(portfolio.average.T)
    w = numpy.asmatrix(random_weights(numpy.asmatrix(portfolio.average.T).shape[1]))
    C = numpy.asmatrix(portfolio.covarianceMatrix)
    
    mu = w * p.T
    sigma = numpy.sqrt(w * C * w.T)
    
    if sigma > 2:
        return random_portfolio(portfolio.average)
    return mu, sigma

def plotRandomPortfolios(n, portfolio):
    n_portfolios = n
    print('Generating',n_portfolios,'random portfolios')
    means, stds = numpy.column_stack([
        random_portfolio(portfolio) 
        for _ in range(n_portfolios)])
    
    plt.plot(stds, means, 'o', markersize=5)
    plt.xlabel('std')
    plt.ylabel('mean')
    plt.title('Mean and standard deviation of returns of randomly generated portfolios')

test = Stock('ibm')

print(numpy.array(test.Data['ibm']))



