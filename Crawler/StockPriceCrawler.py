#coding=utf-8
import time
import logging
from datetime import datetime, timedelta
from Crawler import StockListProvider
from Crawler import Const
import os
import requests
import re

class StockPriceCrawler():
    def __init__(self):
        ''' Make directory if not exist when initialize '''
        self._stock_list_provider = StockListProvider()

    # ===================================================================================================================
    # Utility

    def _data_format(self, row):
        ''' Clean comma and spaces '''
        for index, content in enumerate(row):
            row[index] = re.sub(",", "", content.strip())

        return row

    def _isFloat(self, number):
        try:
            float(number)
            return True
        except ValueError as e:
            return False

    def _get_weekday_string(self, week_day):
        return {
            0: 'MON',
            1: 'TUE',
            2: 'WEN',
            3: 'THR',
            4: 'FRI',
            5: 'SAT',
            6: 'SUN'
        }[week_day]
    #===================================================================================================================
    # Main function

    def _fetch_tse_data(self, date_split, stock_data_dict):
        '''
        Fetch TSE price data
        :param date_split: the date split (year, month, day)
        :param stock_data_dict: {'stock_id,', 'stock_id, date, volumn, open, high, low, close'}
        :return: None
        '''
        date_str = '{0}{1:02d}{2:02d}'.format(date_split[0], date_split[1], date_split[2])
        url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX'
        query_params = {
            'date': date_str,
            'response': 'json',
            'type': 'ALL',
            '_': str(round(time.time() * 1000) - 500)
        }

        # Get json data
        page = requests.get(url, params=query_params)
        if not page.ok:
            return

        content = page.json()

        date_str_ac = '{0}-{1:02d}-{2:02d}'.format(date_split[0], date_split[1], date_split[2])

        if not 'data9' in content:
            return
        else:
            for data in content['data9']:
                stock_id = data[0]
                if self._stock_list_provider.stock_id_exists(stock_id):
                    row = self._data_format([
                        data[0], # stock id
                        date_str_ac, # 日期
                        data[2], # 成交股數
                        data[5], # 開盤價
                        data[6], # 最高價
                        data[7], # 最低價
                        data[8], # 收盤價
                    ])
                    if (int(int(row[2]) / 1000)) == 0 or (not self._isFloat(row[3])):
                        no_data_date = datetime(date_split[0], date_split[1], date_split[2])
                        if no_data_date.weekday() < 5:
                            print(" {0} No data on {1}".format(stock_id, date_str_ac))
                    else:
                        #self._record(data[0].strip(), row)
                        stock_data_dict[stock_id] = row
        return

    def _fetch_otc_data(self, date_split, stock_data_dict):
        date_str = '{0}/{1:02d}/{2:02d}'.format(date_split[0] - 1911, date_split[1], date_split[2])
        ttime = str(int(time.time()*100))
        url = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={}&_={}'.format(date_str, ttime)
        page = requests.get(url)

        if not page.ok:
            return

        result = page.json()

        if result['reportDate'] != date_str:
            return

        data_count = 0
        date_str_ac = '{0}-{1:02d}-{2:02d}'.format(date_split[0], date_split[1], date_split[2])
        for table in [result['mmData'], result['aaData']]:
            for tr in table:
                stock_id = tr[0]
                if self._stock_list_provider.stock_id_exists(stock_id):
                    data_count += 1
                    row = self._data_format([
                        stock_id, # stock id
                        date_str_ac, # 日期
                        tr[8], # 成交股數
                        tr[4], # 開盤價
                        tr[5], # 最高價
                        tr[6], # 最低價
                        tr[2], # 盤價
                       ])
                    if (int(int(row[2])/1000)) == 0 or (not self._isFloat(row[3])):
                        no_data_date = datetime(date_split[0], date_split[1], date_split[2])
                        if no_data_date.weekday() < 5:
                            print(" {0} No data on {1}".format(tr[0], date_str_ac))
                    else:
                        #self._record(tr[0], row)
                        stock_data_dict[stock_id] = row

    # ===================================================================================================================
    # Public method for fetching TSE and OTC data

    def fetch_data(self, datetime_obj):
        stock_data_dict = {}
        self._fetch_tse_data((datetime_obj.year, datetime_obj.month, datetime_obj.day), stock_data_dict)
        self._fetch_otc_data((datetime_obj.year, datetime_obj.month, datetime_obj.day), stock_data_dict)

        return stock_data_dict

# def main():
#     crawler = StockPriceCrawler()
#     first_day = datetime.today()
#     crawler.fetch_data(first_day)
#
# if __name__ == '__main__':
#         main()