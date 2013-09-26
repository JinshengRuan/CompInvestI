import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys as sys

def marketsim(cash, orders, values):
    trades = np.loadtxt(orders, dtype = {'names':('year','month','day','symbol', 'action', 'numbers'), 'formats': ('u2', 'u1', 'u1', 'S10', 'S5', 'i4')} ,delimiter=',')
    symbols = []
    dates = []
    for trade in trades:
        date = dt.datetime(trade[0], trade[1], trade[2], 16)
        dates.append(date)
        symbol = trade[3]
        symbols.append(symbol)

    symbols = list(set(symbols))
    symbols.sort()
    dates.sort()
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

    detailList = []
    totalList = []

    for row in range(len(timestamps)):
        detail = []
        if (row == 0):
            for i in range(len(symbols)):
                detail.append(0)
            detail.append(float(cash))
        else:
            for i in range(len(detailList[row-1])):
                detail.append(detailList[row-1][i])

        timestamp = timestamps[row]
        for trade in trades:
            if (trade[0] == timestamp.year) and (trade[1] == timestamp.month) and (trade[2] == timestamp.day):
                if (trade[4] == 'Buy'):
                    detail[symbols.index(trade[3])] += trade[5]
                    detail[-1] -= trade[5] * na_prices[row][symbols.index(trade[3])]
                elif (trade[4] == 'Sell'):
                    detail[symbols.index(trade[3])] -= trade[5]
                    detail[-1] += trade[5] * na_prices[row][symbols.index(trade[3])]

        detailList.append(detail)

        total = 0.0
        for i in range(len(symbols)):
            total += detail[i] * na_prices[row][i]
        total += detail[-1]
        totalList.append((timestamp.year, timestamp.month, timestamp.day, total))
        
    file = open(values, 'wb')
    np.savetxt(file, totalList, fmt = ['%d', '%d', '%d', '%.0f'], delimiter=',')
    
if __name__ == '__main__':
    marketsim(sys.argv[1], sys.argv[2], sys.argv[3])
