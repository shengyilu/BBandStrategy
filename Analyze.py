from Crawler import *
from Crawler import Const
import csv
import talib as talib
import numpy as np
import pandas as pd
from datetime import datetime

# [stockNumber, date, volume, open, high, low, close, bUp, bMid, bLow, preVolumeAvg5]
def _compute():

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
        preCloseAvg100 = close_sma_100[-2]

        if float(latestCloseData[6]) < preCloseAvg100:
            continue

        volume_sma_5 = np.round(talib.SMA(volumes, timeperiod=5))
        preVolumeAvg5 = volume_sma_5[-2]
        upperband, middleband, lowerband = talib.BBANDS(closePrices, timeperiod=20, nbdevup=2.1, nbdevdn=2.1, matype=0)
        bUpper = np.round(upperband[-1], 2)
        bMid = np.round(middleband[-1], 2)
        bLow = np.round(lowerband[-1], 2)
        bBandWidth = (bUpper - bLow) / bMid



        if float(latestCloseData[2])/1000 < 1000:
            continue

        if float(latestCloseData[2]) < 1.8 * preVolumeAvg5:
            continue

        if bBandWidth > 0.15:
            continue

        if float(latestCloseData[6]) > bUpper and float(latestCloseData[3]) < bUpper:

            target = [latestCloseData[0],
                      round(float(latestCloseData[2])/1000), round(preVolumeAvg5/1000),
                      np.round(float(latestCloseData[2]) / float(preVolumeAvg5), 2),
                      latestCloseData[6],
                      "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

        if float(latestCloseData[6]) > bUpper and float(latestCloseData[3]) > bUpper:
            target = [latestCloseData[0],
                      round(float(latestCloseData[2]) / 1000), round(preVolumeAvg5 / 1000),
                      np.round(float(latestCloseData[2]) / float(preVolumeAvg5), 2),
                      latestCloseData[6],
                      "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '前5日均量', '量倍數', '最後收盤價', '線圖', '週線圖'])
    export_html(df_selected, 'BBandPolicy')

def findAbnormal():
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

        if float(latestCloseData[6]) < 10 or float(latestCloseData[2]/1000) < 1000:
            continue

        close_sma_20 = np.round(talib.SMA(closePrices, timeperiod=20), 2)

        if close_sma_20[-1] < close_sma_20[-2]:
            #print('{} < {}'.format(close_sma_20[-1], close_sma_20[-2]))
            continue

        upperband, middleband, lowerband = talib.BBANDS(closePrices, timeperiod=20, nbdevup=2.1, nbdevdn=2.1, matype=0)
        bUpper = np.round(upperband[-1], 2)
        bMid = np.round(middleband[-1], 2)
        bLow = np.round(lowerband[-1], 2)
        bBandWidth = (bUpper - bLow) / bMid

        if float(latestCloseData[5]) < bLow and float(latestCloseData[6]) > bLow :
            target = [latestCloseData[0],
                      round(float(latestCloseData[2]) / 1000),
                      latestCloseData[6],
                      bLow,
                      "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)


    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', 'BBandLow', '線圖', '週線圖'])
    export_html(df_selected, 'BBandAbnormal')


def findCompressStocks():
    pd.set_option('display.width', 200)
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

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=20), 2)
        volume_sma_5 = np.round(talib.SMA(volumes, timeperiod=5))
        preVolumeAvg5 = volume_sma_5[-2]
        upperband, middleband, lowerband = talib.BBANDS(closePrices, timeperiod=20, nbdevup=2.1, nbdevdn=2.1, matype=0)
        bUpper = np.round(upperband[-1], 2)
        bMid = np.round(middleband[-1], 2)
        bLow = np.round(lowerband[-1], 2)
        bBandWidth = (bUpper - bLow) / bMid

        if float(latestCloseData[6]) < close_sma_100[-1]:
            continue

        if float(latestCloseData[2])/1000 < 1000:
            continue

        # if float(latestCloseData[2]) < 1.8 * preVolumeAvg5:
        #     continue

        if bBandWidth < 0.05:
            target = [latestCloseData[0], round(float(latestCloseData[2]) / 1000), round(preVolumeAvg5 / 1000),
                      latestCloseData[6], bBandWidth, "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '前5日均量', '最後收盤價', 'BBand Width', '布林線圖', '週線圖'])
    export_html(df, 'CompressedBBand')

def findVolumeSpike():

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

        if float(latestCloseData[2])/1000 < 1000:
            continue

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        # if float(latestCloseData[6]) < close_sma_100[-1]:
        #     continue

        volume_sma_5 = np.round(talib.SMA(volumes, timeperiod=5))
        preVolumeAvg5 = volume_sma_5[-2]
        if float(latestCloseData[2]) > 3 * preVolumeAvg5:
            sma100slope = (close_sma_100[-1] - close_sma_100[-2])

            target = [latestCloseData[0], round(float(latestCloseData[2]) / 1000), round(preVolumeAvg5 / 1000),
                      latestCloseData[6], round(float(sma100slope), 2), "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '前5日均量', '最後收盤價', '月線斜率', '布林線圖', '週線圖'])
    df.to_html('{0}/VolumeSpike_{1}.html'.format(Const.STOCK_DATA_FOLDER_NAME, datetime.today().strftime("%Y-%m-%d")),render_links=True)

def findInLowBBand():
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

        if float(latestCloseData[6]) < 10 or float(latestCloseData[2] / 1000) < 1000:
            continue

        close_sma_20 = np.round(talib.SMA(closePrices, timeperiod=20), 2)

        if close_sma_20[-1] < close_sma_20[-2]:
            # print('{} < {}'.format(close_sma_20[-1], close_sma_20[-2]))
            continue

        upperband, middleband, lowerband = talib.BBANDS(closePrices, timeperiod=20, nbdevup=2.1, nbdevdn=2.1, matype=0)
        bUpper = np.round(upperband[-1], 2)
        bMid = np.round(middleband[-1], 2)
        bLow = np.round(lowerband[-1], 2)
        bLowDistance = (float(latestCloseData[6]) - bLow) / bLow

        if float(latestCloseData[6]) < bMid and float(latestCloseData[6]) > bLow :
            target = [latestCloseData[0],
                      round(float(latestCloseData[2]) / 1000),
                      latestCloseData[6],
                      bLowDistance,
                      "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', 'BBandLowDistance', '布林線圖', '週線圖'])
    df.to_html('{0}/BLow.html'.format(Const.STOCK_DATA_FOLDER_NAME, datetime.today().strftime("%Y-%m-%d")), render_links=True)

def findBelowLowBBand():
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

        if float(latestCloseData[6]) < 10 or float(latestCloseData[2] / 1000) < 1000:
            continue

        close_sma_20 = np.round(talib.SMA(closePrices, timeperiod=20), 2)

        # if close_sma_20[-1] < close_sma_20[-2]:
        #     # print('{} < {}'.format(close_sma_20[-1], close_sma_20[-2]))
        #     continue

        upperband, middleband, lowerband = talib.BBANDS(closePrices, timeperiod=20, nbdevup=2.1, nbdevdn=2.1, matype=0)
        bUpper = np.round(upperband[-1], 2)
        bMid = np.round(middleband[-1], 2)
        bLow = np.round(lowerband[-1], 2)
        bLowDistance = (float(latestCloseData[6]) - bLow) / bLow

        if float(latestCloseData[6]) < bLow:
            target = [latestCloseData[0],
                      round(float(latestCloseData[2]) / 1000),
                      latestCloseData[6],
                      bLowDistance,
                      "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', 'BBandLowDistance', '布林線圖', '週線圖'])
    df.to_html('{0}/BelowLow.html'.format(Const.STOCK_DATA_FOLDER_NAME, datetime.today().strftime("%Y-%m-%d")), render_links=True)

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

def _confirm_unique(stock_history_dict_list):
    no_dupes = [x for n, x in enumerate(stock_history_dict_list) if x not in stock_history_dict_list[:n]]
    return no_dupes

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
    df.to_html('{0}/{1}_{2}.html'.format(Const.STOCK_DATA_FOLDER_NAME, fileName, datetime.today().strftime("%Y-%m-%d")), render_links=True)


def main():
    _compute()
    findAbnormal()
    findCompressStocks()
    findVolumeSpike()
    findCompressStocks()
    findInLowBBand()
    findBelowLowBBand()


if __name__ == '__main__':
    main()