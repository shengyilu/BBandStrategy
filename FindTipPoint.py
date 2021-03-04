from Crawler import *
from Crawler import Const
import csv
import talib as talib
import numpy as np
import pandas as pd
import datetime as dt

def _findLowTipPoint():
    stock_list_provider = StockListProvider()
    stock_id_list = stock_list_provider.get_stock_id_list()
    currentWeekNumber = int(_get_current_weeknumber())
    selectedStocks = []
    selectedStocks_published = []
    for stock_id in stock_id_list:
        if stock_id in Const.STOCK_IGNORE_LIST:
            continue
        try:
            df = _read_raw_prices(stock_id)
            closePrices = df.iloc[:, 6].astype('float').values
            close_sma_100 = np.round(talib.SMA(closePrices, timeperiod=100), 2)
            
        
            latestCloseData = _read_latest_price_by_id(stock_id)
            lastWeekPrice = _get_week_k_bar(stock_id, currentWeekNumber - 1)
            if not lastWeekPrice:
                continue
            #print(lastWeekPrice)
            last2WeekPrice = _get_week_k_bar(stock_id, currentWeekNumber - 2)
            if not last2WeekPrice: 
                continue
            #print(last2WeekPrice)
            # if last2WeekPrice[-1] > close_sma_100[-1]:
            #     continue
            # last2WeekPrice should be black K bar
            if (last2WeekPrice[-1] - last2WeekPrice[0] > 0): 
                continue
            # lastWeekPrice should be red K bar
            if (lastWeekPrice[-1] - lastWeekPrice[0] < 0):
                continue

            if (lastWeekPrice[-1] < last2WeekPrice[0]): 
                continue

            target = [latestCloseData[0],
                  round(float(latestCloseData[2])/1000),
                  latestCloseData[6],
                  "https://histock.tw/stock/tchart.aspx?no={}&m=b".format(latestCloseData[0]),
                  "http://jsjustweb.jihsun.com.tw/Z/ZC/ZCW/ZCW_{}_W.djhtm".format(latestCloseData[0])]
        
            selectedStocks.append(target)        
        except IOError as err:
            continue
        
        
    df_selected = pd.DataFrame(selectedStocks, columns=['股號', '成交量', '最後收盤價', '線圖', '週線圖'])
    export_html(df_selected, '向上轉折點選股')


        
## Util
def _get_current_weeknumber():
    today_str = dt.datetime.now().strftime("%Y-%m-%d")
    return _get_weeknumber_by_date(today_str)

def _get_weeknumber_by_date(date_str):
    '''
    Get week number according to data input
    :param date_str: 2017-01-01 (format)
    :return: week number
    '''
    datetime_obj = _convert_str_to_date(date_str)
    return datetime_obj.strftime('%U')

def _convert_str_to_date(date_str):
    date_split = date_str.split('-')
    date_time = dt.datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]))
    return date_time

def _get_week_k_bar(stock_id, week_number):
    dateRange = _get_dates_from_week_number(week_number)
    week_k_bar = _select_price_data_by_dates(stock_id, dateRange) 
    return week_k_bar

def _get_dates_from_week_number(week_number):
    dateStrWeekFormat = "2020-W{}".format(week_number)
    dates = []
    for i in range(5):
        dateObj = dt.datetime.strptime(dateStrWeekFormat + '-{}'.format(i), "%Y-W%W-%w")
        dateStr = dateObj.strftime("%Y-%m-%d")
        dates.append(dateStr)
    
    return dates

def _select_price_data_by_dates(stock_id, date_range):
    stock_id_price_path = "{0}/{1}-raw.csv".format(Const.STOCK_HISTORY_FOLDER_PATH, stock_id)
    df = pd.read_csv(stock_id_price_path, header=None)
    df.columns = ['stock', 'date', 'volume', 'open', 'high', 'low', 'close']
    df = df.loc[df['date'].isin(date_range)]
    price_data = []
    if not df.empty:
        price_data.append(df['open'].iloc[0])
        price_data.append(df['high'].max())
        price_data.append(df['low'].min())
        price_data.append(df['close'].iloc[-1])
    return price_data

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


def _read_latest_price_by_id(stock_id):
    '''
    Read raw data from /data/history/XXXX.csv
    :param stock_id: stock id
    :return: a list of dictionary (each day)
    '''
    stock_id_price_path = "{0}/{1}-raw.csv".format(Const.STOCK_HISTORY_FOLDER_PATH, stock_id)

    df = pd.read_csv(stock_id_price_path, header=None)
    latestCloseData = df.iloc[-1,:].values
    return latestCloseData  

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
    df.to_html('{0}/{1}_{2}.html'.format('selection', fileName, dt.datetime.today().strftime("%Y-%m-%d")), render_links=True)


def main():
    _findLowTipPoint() 


if __name__ == '__main__':
    main()