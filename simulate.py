# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def simulate(dt_start, dt_end, ls_symbols, ls_alloc):
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values

    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]

    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()

    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets)

    portfolio_daily_rets = np.dot(na_rets, ls_alloc)

    pdr_sig = np.std(portfolio_daily_rets)

    pdr_mu = np.mean(portfolio_daily_rets)

    sharpe_ratio = np.sqrt(252) * pdr_mu / pdr_sig
    
    cum_rets = np.cumprod(portfolio_daily_rets + 1)

    return pdr_sig, pdr_mu, sharpe_ratio, cum_rets[-1]

def main():
    start1 = dt.datetime(2011, 1, 1)
    end1 = dt.datetime(2011,12,31)
    symbols1 = ['AAPL', 'GLD', 'GOOG', 'XOM']
    alloc1 = [0.4, 0.4, 0.0, 0.2]

    print simulate(start1, end1, symbols1, alloc1)

    start2 = dt.datetime(2010,1,1)
    end2 = dt.datetime(2010,12,31)
    symbols2 = ['AXP', 'HPQ', 'IBM', 'HNZ']
    alloc2 = [0.0, 0.0, 0.0, 1.0]
    
    print simulate(start2, end2, symbols2, alloc2)

    maxsr=float("-inf")
    maxalloc=""
    n=10
    slist= ['BRCM', 'TXN', 'IBM', 'HNZ']
    sd=dt.datetime(2010, 1, 1)
    se=dt.datetime(2010, 12, 31)

    for i in range(n):
        for j in range(n):
            for k in range(n):
                if 1-((i+j+k)/float(n))>=0:
                    print i/float(n), j/float(n), k/float(n), 1-((i+j+k)/float(n))
                    salloc=[round(i/float(n),2), round(j/float(n),2), round(k/float(n),2), round(1-((i+j+k)/float(n)),2)]
                    sig,mu,sr,cr=simulate(sd,se,slist ,salloc)
                    if sr>maxsr:
                        maxsr=sr
                        maxalloc=salloc
    print maxalloc,maxsr

if __name__ == '__main__':
    main()
