#coding=utf-8

from Crawler import *
from Crawler import Const
import csv
import talib as talib
import numpy as np
import pandas as pd
from datetime import datetime
import os

def _get_weeknumber_by_date(self, date_str):
    '''
    Get week number according to data input
    :param date_str: 2017-01-01 (format)
    :return: week number
    '''
    datetime_obj = self._convert_str_to_date(date_str)
    return datetime_obj.strftime('%U')


def _convert_str_to_date(self, date_str):
    date_split = date_str.split('-')
    date_time = datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]))
    return date_time


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

def _read_raw_price_by_id_2(stock_id):
    '''
    Read raw data from /data/history/XXXX.csv
    :param stock_id: stock id
    :return: a list of dictionary (each day)
    '''
    stock_id_price_path = "{0}/{1}-raw.csv".format(Const.STOCK_HISTORY_FOLDER_PATH, stock_id)

    df = pd.read_csv(stock_id_price_path, header=None)
    df = df.tail(110)
    latestCloseData = df.iloc[-1,:].values
    startCloseData = df.iloc[-5, :].values

    volume = df.iloc[:, 2].astype('float').values
    closePrice = df.iloc[:, 6].astype('float').values
    return startCloseData, latestCloseData, closePrice, volume

def _read_raw_price_by_id_and_days(stock_id, days):
    '''
    Read raw data from /data/history/XXXX.csv
    :param stock_id: stock id
    :return: a list of dictionary (each day)
    '''
    stock_id_price_path = "{0}/{1}-raw.csv".format(Const.STOCK_HISTORY_FOLDER_PATH, stock_id)

    df = pd.read_csv(stock_id_price_path, header=None)
    df = df.tail(110)
    df_days =df.tail(days)

    volume = df.iloc[:, 2].astype('float').values
    closePrice = df.iloc[:, 6].astype('float').values
    return df_days, closePrice, volume

def _read_raw_prices(stock_id):
    '''
    Read raw data from /data/history/XXXX.csv
    :param stock_id: stock id
    :return: a list of dictionary (each day)
    '''
    stock_id_price_path = "{0}/{1}-raw.csv".format(Const.STOCK_HISTORY_FOLDER_PATH, stock_id)

    df = pd.read_csv(stock_id_price_path, header=None)
    df = df.tail(110)

    return df

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
    folder = createFolderIfNeed(datetime.today().strftime("%Y-%m-%d"))
    df_select = df_select.set_index('股號')
    df_share_capital = getCapitalInfo(df_select.index.values)
    df = pd.merge(df_share_capital, df_select, left_index=True, right_index=True)
    pd.set_option('display.max_colwidth', -1)
    df.to_html('{0}/{1}_{2}.html'.format(folder, fileName, datetime.today().strftime("%Y-%m-%d")), render_links=True)


def createFolderIfNeed(name):
    folder = '{0}/{1}'.format('selection', name)
    if not os.path.isdir(folder):
        os.mkdir(folder)
    return folder
#-----------------------------------------------------------------------------------------------------------------------
# 策略

def _findBBandPolicy():
    '''
    根據阿水布林通道 + 20週均線
    條件: 股價在 20 週線上 / 股價穿過布林上軌道 / 量大於 1000 張 / 量大於 5日均量 1.8 倍
    '''

    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    selectedStocks = []
    selectedStocks_published = []
    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        try:
            latestCloseData, closePrices, volumes = _read_raw_price_by_id(stock_id)
        except IOError as err:
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

        if float(latestCloseData[6]) > bUpper:
            target = [latestCloseData[0],
                      round(float(latestCloseData[2])/1000), round(preVolumeAvg5/1000),
                      np.round(float(latestCloseData[2]) / float(preVolumeAvg5), 2),
                      latestCloseData[6],
                      "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

            target_published = [latestCloseData[0],
                      round(float(latestCloseData[2]) / 1000), round(preVolumeAvg5 / 1000),
                      np.round(float(latestCloseData[2]) / float(preVolumeAvg5), 2),
                      latestCloseData[6]]
            selectedStocks_published.append(target_published)

    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '前5日均量', '量倍數', '最後收盤價', '線圖', '週線圖'])
    export_html(df_selected, '阿水一式')

def _findAbove20W():
    '''
    根據林恩如的長線聚寶盆概念
    條件: 股價在 20 週線上 量大於 1000 張
    '''
    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    selectedStocks = []
    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        try:
            latestCloseData, closePrices, volumes = _read_raw_price_by_id(stock_id)
        except IOError as err:
            continue
        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        closeAvg100 = close_sma_100[-1]

        # 略去收盤價在 20週線 下
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
        export_html(df_selected, '20週長線選股')

def _findCrossDay20FromBBandLow():
    '''
    根據我們發現的pattern，強勢股回檔跌破月線後，從布林下軌道反攻上月線的個股
    條件: 股價在 20 週線上 / 股價從布林下軌道向上穿過月線 / 量大於 1000 張 / 量大於 5日均量 1.8 倍
    '''
    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    selectedStocks = []

    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        try:
            df_days, closePrices, volumes = _read_raw_price_by_id_and_days(stock_id, 2)
        except IOError as err:
            continue

        latestCloseData = df_days.iloc[-1, :].values
        previousData = df_days.iloc[-2, :].values

        if float(latestCloseData[2] / 1000) < 1000:
            continue

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        if float(latestCloseData[6]) < close_sma_100[-1]:
            continue

        close_sma_20 = np.round(talib.SMA(closePrices, timeperiod=20), 2)

        if float(previousData[6]) < close_sma_20[-1] and float(latestCloseData[6]) > close_sma_20[-1]:
            target = [latestCloseData[0],
                      round(float(latestCloseData[2]) / 1000),
                      latestCloseData[6],
                      "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', '布林線圖', '週線圖'])
    #df.to_html('{0}/findCrossDay20.html'.format(Const.STOCK_DATA_FOLDER_NAME, datetime.today().strftime("%Y-%m-%d")), render_links=True)
    export_html(df, '強勢回檔反彈股')


def _findInLowBBandAndGoUP():
    '''
    根據我們發現的pattern，強勢股回檔跌破月線後，從布林下軌道有反彈訊號的個股
    條件: 股價在 20 週線上 / 前一天收盤在布林下軌道，今日收實體紅k蓋過前一日高價 / 量大於 1000 張
    '''
    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    selectedStocks = []

    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        try:
            df = _read_raw_prices(stock_id)
        except IOError as err:
            continue

        latestCloseData = df.iloc[-1, :].values
        previousData = df.iloc[-2, :].values
        closePrices = df.iloc[:, 6].astype('float').values

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        if float(latestCloseData[6]) < close_sma_100[-1]:
            continue

        # 水餃股，張數小於1000不考慮
        if float(latestCloseData[6]) < 10 or float(latestCloseData[2] / 1000) < 1000:
            continue

        if float(latestCloseData[6]) < float(previousData[4]):
            continue

        if float(latestCloseData[6]) < float(latestCloseData[3]):
            continue

        upperband, middleband, lowerband = talib.BBANDS(closePrices, timeperiod=20, nbdevup=2.1, nbdevdn=2.1, matype=0)
        bMid = np.round(middleband[-1], 2)
        bLow = np.round(lowerband[-1], 2)

        if previousData[6] < bMid and float(latestCloseData[6]) > previousData[6]:
            target = [latestCloseData[0],
                      round(float(latestCloseData[2]) / 1000),
                      latestCloseData[6],
                      "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', '布林線圖', '週線圖'])
    export_html(df, 'BLow')


def _findTurningPointInLowBBand():
    
    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    selectedStocks = []

    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        try:
            df = _read_raw_prices(stock_id)
        except IOError as err:
            continue

        latestCloseData = df.iloc[-1, :].values
        previousData = df.iloc[-2, :].values
        closePrices = df.iloc[:, 6].astype('float').values

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)

        # 水餃股，張數小於1000不考慮
        if float(latestCloseData[6]) < 10 or float(latestCloseData[2] / 1000) < 1000:
            continue

        upperband, middleband, lowerband = talib.BBANDS(closePrices, timeperiod=20, nbdevup=2.1, nbdevdn=2.1, matype=0)
        bMid = np.round(middleband[-1], 2)
        bLow = np.round(lowerband[-1], 2)

        if float(previousData[5]) < bLow and float(latestCloseData[6]) > bLow:
            target = [latestCloseData[0],
                      round(float(latestCloseData[2]) / 1000),
                      latestCloseData[6],
                      "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', '布林線圖', '週線圖'])
    export_html(df, '在下軌道以下反轉')

def main():
    _findBBandPolicy()
    _findAbove20W()
    _findCrossDay20FromBBandLow()
    _findInLowBBandAndGoUP()
    _findTurningPointInLowBBand()


if __name__ == '__main__':
    main()