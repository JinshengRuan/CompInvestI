import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys as sys

def analyze(values, benchmark):
    funds = np.loadtxt(values, dtype = {'names':('year','month','day','total'), 'formats': ('u2', 'u1', 'u1', 'i4')} ,delimiter=',')

    dates = []
    totals = []
    for fund in funds:
        date = dt.datetime(fund[0], fund[1], fund[2], 16)
        dates.append(date)
        totals.append(fund[3])

    symbols = []
    symbols.append(benchmark)
    dt_start = dates[0]
    dt_end = dates[-1]
    timeofday = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(dt_start, dt_end, timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(timestamps, symbols, keys)
    d_data = dict(zip(keys, ldf_data))

    for key in keys:
        d_data[key] = d_data[key].fillna(method='ffill')
        d_data[key] = d_data[key].fillna(method='bfill')
        d_data[key] = d_data[key].fillna(1.0)

    na_prices = d_data['close'].values
    spx_prices = na_prices[:,0]

    bench = totals[0] / spx_prices[0]

    allValues = []
    for row in range(len(dates)):
        allValue = []
        allValue.append(totals[row])
        allValue.append(spx_prices[row] * bench)
        allValues.append(allValue)

    plt.clf()
    plt.plot(dates, allValues)
    plt.ylabel('Value')
    plt.xlabel('Date')
    plt.savefig('fund.pdf', format='pdf')

    totalRet_fund = float(totals[-1]) / float(totals[0])
    totalRet_spx = spx_prices[-1] / spx_prices[0]

    dailyRets_fund = []
    dailyRets_fund.append(0)
    dailyRets_spx = []
    dailyRets_spx.append(0)

    for i in range(1, len(totals)-1):
        dailyRets_fund.append(float(totals[i]) / float(totals[i-1]) - 1)

    for i in range(1, len(spx_prices)-1):
        dailyRets_spx.append(spx_prices[i] / spx_prices[i-1] - 1)

    std_fund = np.std(dailyRets_fund)
    std_spx = np.std(dailyRets_spx)

    mean_fund = np.average(dailyRets_fund)
    mean_spx = np.average(dailyRets_spx)

    sharpe_fund = np.sqrt(252) * mean_fund / std_fund
    sharpe_spx = np.sqrt(252) * mean_spx / std_spx

    print sharpe_fund, sharpe_spx, totalRet_fund, totalRet_spx, std_fund, std_spx, mean_fund, mean_spx
        
if __name__ == '__main__':
    analyze(sys.argv[1], sys.argv[2])
