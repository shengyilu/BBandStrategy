#coding=utf-8

from Crawler import *
from Crawler import Const
import csv
import talib as talib
import numpy as np
import pandas as pd
from datetime import datetime
import os
import webbrowser

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

def _findCross20W():
    '''
    找尋近一週穿越20週均線的股票
    '''
    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    selectedStocks = []
    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        #stock_id = 1101
        try:
            latestCloseData, closePrices, volumes = _read_raw_price_by_id(stock_id)
        except IOError as err:
            continue

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        closeAvg100 = close_sma_100[-1]

        # print("Stock id = {0}".format(stock_id))
        # print(close_sma_100) 
        # print(closePrices[-5:-1]) 
        
        # print("Stock id = {0}, n = {1}".format(stock_id, n))
        # break
        # 略去收盤價在 20週線 下
        if float(latestCloseData[6]) < closeAvg100:
            continue

        n = 5
        while n > 1:
            if float(closePrices[-1 * n]) < closeAvg100:
                break
            else:
                n -= 1

        #print(n) 
        if n == 1:
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
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_D.djhtm".format(latestCloseData[0]),
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]

        selectedStocks.append(target) 
        webbrowser.open("http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0]), new=0, autoraise=True)
        
    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '週均量', '量倍數', '最後收盤價', '線圖', '週線圖'])
    export_html(df_selected, '股價剛穿過20週均線')

def _findClimbing20W(weekCount):
    '''
    找尋20週線連續爬升的股票
    '''
    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    selectedStocks = []
    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        # stock_id = 1210
        try:
            latestCloseData, closePrices, volumes = _read_raw_price_by_id(stock_id)
        except IOError as err:
            continue
        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        closeAvg100 = close_sma_100[-1]

        # print("Stock id = {0}, closeAvg100 = {1}".format(stock_id, closeAvg100))
        # print(close_sma_100)
        
        n = weekCount
        while n > 1:
            dayth = 0 - n
            if float(close_sma_100[dayth]) - float(close_sma_100[dayth + 1]) < 0:
                n -= 1
                continue
            else:
                break
        
        # print("Stock id = {0}, n = {1}".format(stock_id, n))
        # break
        if n > 1:
            continue

        # 略去收盤價在 20週線 下
        # if float(latestCloseData[6]) < closeAvg100:
        #     continue

        volumes_sma_20 = np.round(talib.SMA(volumes, timeperiod=20), 2)
        volumeAvg20 = volumes_sma_20[-1]

        if (volumeAvg20 / 1000) < 1000:
            continue

        target = [latestCloseData[0],
                  round(float(latestCloseData[2]) / 1000),
                  round(volumeAvg20 / 1000),
                  round(float(latestCloseData[2]) / volumeAvg20, 2),
                  latestCloseData[6],
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_D.djhtm".format(latestCloseData[0]),
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]

        selectedStocks.append(target) 
        webbrowser.open("http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0]), new=0, autoraise=True)
        
    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '週均量', '量倍數', '最後收盤價', '線圖', '週線圖'])
    export_html(df_selected, '20週均連5週爬升')
        
def _find5DUpCross20D():
    '''
    找尋5日均向上穿越20日均
    '''
    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    selectedStocks = []
    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        #stock_id = 1101
        try:
            latestCloseData, closePrices, volumes = _read_raw_price_by_id(stock_id)
        except IOError as err:
            continue

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        close_sma_5 = np.round(talib.SMA(closePrices, timeperiod=5), 2)
        close_sma_20 = np.round(talib.SMA(closePrices, timeperiod=20), 2)
        
        closeAvg100 = close_sma_100[-1]

        # print("Stock id = {0}".format(stock_id))
        # print(close_sma_100) 
        # print(closePrices[-5:-1]) 
        
        # print("Stock id = {0}, n = {1}".format(stock_id, n))
        # break
        # 略去收盤價在 20週線 下
        if float(latestCloseData[6]) < closeAvg100:
            continue

        volumes_sma_20 = np.round(talib.SMA(volumes, timeperiod=20), 2)
        volumeAvg20 = volumes_sma_20[-1]

        if (volumeAvg20 / 1000) < 1000:
            continue
        
        if float(close_sma_5[-2]) < float(close_sma_20[-1]) and float(close_sma_5[-1]) >= float(close_sma_20[-1]):
            target = [latestCloseData[0],
                  round(float(latestCloseData[2]) / 1000),
                  round(volumeAvg20 / 1000),
                  round(float(latestCloseData[2]) / volumeAvg20, 2),
                  latestCloseData[6],
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_D.djhtm".format(latestCloseData[0]),
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target) 
  
    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '週均量', '量倍數', '最後收盤價', '日線圖', '週線圖'])
    export_html(df_selected, '5日均向上穿越20日均')

def _findUpClose5D():
    '''
    找尋穿越5日線
    '''
    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    selectedStocks = []
    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        #stock_id = 1101
        try:
            latestCloseData, closePrices, volumes = _read_raw_price_by_id(stock_id)
        except IOError as err:
            continue

        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        close_sma_5 = np.round(talib.SMA(closePrices, timeperiod=5), 2)
        close_sma_20 = np.round(talib.SMA(closePrices, timeperiod=20), 2)
        
        closeAvg100 = close_sma_100[-1]

        # print("Stock id = {0}".format(stock_id))
        # print(close_sma_100) 
        # print(closePrices[-5:-1]) 
        
        # print("Stock id = {0}, n = {1}".format(stock_id, n))
        # break
        # 略去收盤價在 20週線 下
        if float(latestCloseData[6]) < closeAvg100:
            continue

        volumes_sma_20 = np.round(talib.SMA(volumes, timeperiod=20), 2)
        volumeAvg20 = volumes_sma_20[-1]

        if (volumeAvg20 / 1000) < 1000:
            continue
        
        if float(close_sma_5[-1]) > float(latestCloseData[3]) and float(close_sma_5[-1]) < float(latestCloseData[6]):
            target = [latestCloseData[0],
                  round(float(latestCloseData[2]) / 1000),
                  round(volumeAvg20 / 1000),
                  round(float(latestCloseData[2]) / volumeAvg20, 2),
                  latestCloseData[6],
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_D.djhtm".format(latestCloseData[0]),
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target) 
  
    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '週均量', '量倍數', '最後收盤價', '日線圖', '週線圖'])
    export_html(df_selected, '股價向上穿過5日線')


def main():
    _findClimbing20W(10)
    _findCross20W()
    _find5DUpCross20D() 
    _findUpClose5D()


if __name__ == '__main__':
    main()