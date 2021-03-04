from Crawler import *
from Crawler import Const
import csv
import talib as talib
import numpy as np
import pandas as pd
from datetime import datetime


# [stockNumber, date, volume, open, high, low, close]
def _longLinePolicy():
    stockShareCapitalPath = "{0}/{1}".format(Const.STOCK_DATA_FOLDER_NAME, 'ShareCapital.csv')
    df_share_capital = pd.read_csv(stockShareCapitalPath)

    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()

    selectedStocks = []
    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        try:
            latestCloseData, closePrices, volumes = _read_raw_price_by_id(stock_id)
        except FileNotFoundError as err:
            continue

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        closeAvg100 = close_sma_100[-1]

        if float(latestCloseData[6]) < closeAvg100:
            continue

        volumes_sma_20 = np.round(talib.SMA(volumes, timeperiod=20), 2)
        volumeAvg20 = volumes_sma_20[-1]

        if (volumeAvg20 / 1000) < 1000:
            continue

        target = [latestCloseData[0],
                  round(float(latestCloseData[2]) / 1000),
                  round(volumeAvg20 / 1000),
                  round(float(latestCloseData[2]) / volumeAvg20, 2),
                  latestCloseData[6],
                  "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]

        selectedStocks.append(target)

    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '週均量', '量倍數', '最後收盤價', '線圖', '週線圖'])
    export_html(df_selected, 'LoneLineMoney')


def _longLinePolicyReverse():
    stockShareCapitalPath = "{0}/{1}".format(Const.STOCK_DATA_FOLDER_NAME, 'ShareCapital.csv')
    df_share_capital = pd.read_csv(stockShareCapitalPath)

    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()

    selectedStocks = []
    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        try:
            latestCloseData, closePrices, volumes = _read_raw_price_by_id(stock_id)
        except FileNotFoundError as err:
            continue

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        closeAvg100 = close_sma_100[-1]

        if float(latestCloseData[6]) > closeAvg100 or float(latestCloseData[6]) < 10:
            continue

        volumes_sma_20 = np.round(talib.SMA(volumes, timeperiod=20), 2)
        volumeAvg20 = volumes_sma_20[-1]

        if (volumeAvg20 / 1000) < 1000:
            continue

        target = [latestCloseData[0],
                  round(float(latestCloseData[2]) / 1000),
                  round(volumeAvg20 / 1000),
                  round(float(latestCloseData[2]) / volumeAvg20, 2),
                  latestCloseData[6],
                  "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]

        selectedStocks.append(target)

    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '週均量', '量倍數', '最後收盤價', '線圖', '週線圖'])
    export_html(df_selected, 'LoneLineMoneyReverse')

# Utility
def getCapitalInfo(stocks):
    stockShareCapitalPath = "{0}/{1}".format(Const.STOCK_DATA_FOLDER_NAME, 'ShareCapital.csv')
    df_share_capital = pd.read_csv(stockShareCapitalPath)
    df_share_capital = df_share_capital.loc[df_share_capital['代號'].isin(stocks)]
    df_share_capital = df_share_capital.set_index('代號')
    return df_share_capital

def export_html(df_select, fileName):
    df_select = df_select.set_index('股號')
    df_share_capital = getCapitalInfo(df_select.index.values)
    df = pd.merge(df_share_capital, df_select, left_index=True, right_index=True)
    pd.set_option('display.max_colwidth', -1)
    df.to_html('{0}/{1}_{2}.html'.format(Const.STOCK_DATA_FOLDER_NAME, fileName, datetime.today().strftime("%Y-%m-%d")))
    ##df.to_excel('{0}/{1}_{2}.xlsx'.format(Const.STOCK_DATA_FOLDER_NAME, fileName, datetime.today().strftime("%Y-%m-%d")))

def _read_raw_price_by_id(stock_id):
    '''
    Read raw data from /data/history/XXXX.csv
    :param stock_id: stock id
    :return: a list of dictionary (each day)
    '''
    stock_id_price_path = "{0}/{1}-raw.csv".format(Const.STOCK_HISTORY_FOLDER_PATH, stock_id)

    df = pd.read_csv(stock_id_price_path, header=None)
    df = df.tail(110)
    latestCloseData = df.iloc[-1,:].values
    volume = df.iloc[:, 2].astype('float').values
    closePrice = df.iloc[:, 6].astype('float').values
    return latestCloseData, closePrice, volume

def main():
    _longLinePolicyReverse()


if __name__ == '__main__':
    main()