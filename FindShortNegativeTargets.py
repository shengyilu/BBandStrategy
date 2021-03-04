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
def _findVolumeSpikePriceUp():
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

        close_sma_20  = np.round(talib.SMA(closePrices, timeperiod=20), 2)
        closeAvg20 = close_sma_20[-1]
        if float(latestCloseData[6]) > closeAvg20:
            continue

        volume_sma_60 = np.round(talib.SMA(volumes, timeperiod=60))
        # 張數小於1000不考慮
        if float(latestCloseData[2] / 1000) < 1000:
            continue

        # 漲的不看
        if float(latestCloseData[6]) > float(latestCloseData[3]):
            continue

        preVolumeAvg60 = volume_sma_60[-2]
        if float(latestCloseData[2]) > 2 * preVolumeAvg60:
            target = [latestCloseData[0],
                    round(float(latestCloseData[2]) / 1000),
                    latestCloseData[6],
                    "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                    "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)
    
    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', '布林線圖', '週線圖'])
    export_html(df, '爆大量收黑')



def _findCross20MAWithVolume():
    
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
        close_sma_20  = np.round(talib.SMA(closePrices, timeperiod=20), 2)
        volume_sma_60 = np.round(talib.SMA(volumes, timeperiod=60))

        # 張數小於1000不考慮
        if float(latestCloseData[2] / 1000) < 1000:
            continue

        closeAvg20 = close_sma_20[-1]
        preVolumeAvg60 = volume_sma_60[-2]
        if float(latestCloseData[6]) < closeAvg20 and float(latestCloseData[3]) > closeAvg20:
            if float(latestCloseData[2]) > preVolumeAvg60:
                target = [latestCloseData[0],
                        round(float(latestCloseData[2]) / 1000),
                        latestCloseData[6],
                        "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                        "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
                selectedStocks.append(target)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', '布林線圖', '週線圖'])
    export_html(df, '楊雲翔-帶量突破20MA_空')

def main():
    _findCross20MAWithVolume()
    _findVolumeSpikePriceUp()



if __name__ == '__main__':
    main()