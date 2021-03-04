from Crawler import *
from Crawler import Const
import csv
import talib as talib
import numpy as np
import pandas as pd
from datetime import datetime

def _findPositiveOrder():
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

        if float(latestCloseData[2])/1000 < 1000:
            continue
        
        close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
        close_sma_20 = np.round(talib.SMA(closePrices, timeperiod=20), 2)
        close_sma_5 = np.round(talib.SMA(closePrices, timeperiod=5), 2)

        preCloseAvg100 = close_sma_100[-2]
        preCloseAvg20 = close_sma_20[-2]
        preCloseAvg5 = close_sma_5[-2]       

        if preCloseAvg100 > preCloseAvg20:
            continue

        if preCloseAvg20 > preCloseAvg5:
            continue


        target = [latestCloseData[0],
                  round(float(latestCloseData[2])/1000),
                  latestCloseData[6],
                  "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
        
        selectedStocks.append(target)

    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', '線圖', '週線圖'])
    export_html(df_selected, '多頭排列')

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
        if float(latestCloseData[6]) < close_sma_100[-1]:
            continue

        volume_sma_5 = np.round(talib.SMA(volumes, timeperiod=5))
        preVolumeAvg5 = volume_sma_5[-2]
        if float(latestCloseData[2]) > 3 * preVolumeAvg5:

            target = [latestCloseData[0], round(float(latestCloseData[2]) / 1000), round(preVolumeAvg5 / 1000),
                      latestCloseData[6], "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_d.djhtm".format(latestCloseData[0]),
                      "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
            selectedStocks.append(target)

    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '前5日均量', '最後收盤價', '日線圖', '週線圖'])
    #df.to_html('{0}/VolumeSpike_{1}.html'.format(Const.STOCK_DATA_FOLDER_NAME, datetime.today().strftime("%Y-%m-%d")),render_links=True)
    export_html(df, 'VolumeSpike')

## Util
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
    df.to_html('{0}/{1}_{2}.html'.format('selection', fileName, datetime.today().strftime("%Y-%m-%d")), render_links=True)


def main():
    findVolumeSpike()
    _findPositiveOrder()


if __name__ == '__main__':
    main()