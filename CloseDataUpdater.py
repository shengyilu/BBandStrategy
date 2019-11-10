from Crawler import *
from datetime import datetime, timedelta
from Crawler import Const
import os
import shutil
import csv
import time
import pandas as pd

class CloseDataUpdater():

    STOCK_DAILY_UPDATE_FOLDER_NAME = 'daily'
    STOCK_DAILY_UPDATE_FOLDER_PATH = '{0}/{1}'.format(Const.STOCK_DATA_FOLDER_NAME, STOCK_DAILY_UPDATE_FOLDER_NAME)

    def __init__(self):
        self._stock_list_provider = StockListProvider()
        self._crawler = StockPriceCrawler()
        self._init_data_folder()

    def _init_data_folder(self, is_remove_old = False):
        # create root data folder if not exists
        if not os.path.isdir(Const.STOCK_DATA_FOLDER_NAME):
            os.mkdir(Const.STOCK_DATA_FOLDER_NAME)
        if is_remove_old:
            self._remove_old_data(CloseDataUpdater.STOCK_DAILY_UPDATE_FOLDER_PATH)
            os.mkdir(CloseDataUpdater.STOCK_DAILY_UPDATE_FOLDER_PATH)

    def _remove_old_data(self, file_name):
        if os.path.isdir(file_name):
            shutil.rmtree(file_name)

        if os.path.isfile(file_name):
            os.remove(file_name)
    # ==================================================================================================================
    # Utility
    def _convert_datetime_obj(self, date_str):
        '''
        Convert xxxx-xx-xx format data string to datetime obj
        :param date_str: xxxx-xx-xx
        :return: datetime object
        '''
        date_split = date_str.split('-')
        date_time = datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]))
        return date_time

    def _read_data(self, stock_id):
        stock_history_list = []
        stock_id_price_path = "{0}/{1}-raw.csv".format(CloseDataUpdater.STOCK_DAILY_UPDATE_FOLDER_PATH, stock_id)
        try:
            file = open(stock_id_price_path, 'r')
            csv_cursor = csv.reader(file)
            for row in csv_cursor:
                stock_history_list.append(row)
        except FileNotFoundError as err:
            print("No data of {0}-raw".format(stock_id))

        return stock_history_list

    def _save_data(self, stock_data_dict):
        stock_list = self._stock_list_provider.get_stock_id_list()
        for stock_id in stock_list:
            if stock_id in stock_data_dict:
                stock_id_price_path = "{0}/{1}-raw.csv".format(Const.STOCK_HISTORY_FOLDER_PATH, stock_id)
                try:
                    df = pd.read_csv(stock_id_price_path, header=None)
                    row = pd.Series(stock_data_dict[stock_id])
                    df = df.append(row, ignore_index=True)
                    df = df.tail(110)
                    df.to_csv(stock_id_price_path, index=False, header=False)
                except IOError as err:
                    print("No data of {0}-raw".format(stock_id))



   # ==================================================================================================================
    # Fetch close data
    def _crawl_data_since_date(self, datetime_obj):
        if datetime_obj == datetime.today():
            print('Price info already up-to date')
            return

        stock_history_list = []
        while True:
            datetime_obj += timedelta(days=1)
            if datetime_obj > datetime.today():
                break
            time.sleep(10)
            stock_day_data_dict = self._crawler.fetch_data(datetime_obj)
            self._save_data(stock_day_data_dict)

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

    # ==================================================================================================================
    def _getLastestDate(self):
        stock_id_price_path = "{0}/{1}-raw.csv".format(Const.STOCK_HISTORY_FOLDER_PATH, '0050')
        df = pd.read_csv(stock_id_price_path, header=None)
        latestRow = df.iloc[-1:]
        return self._convert_datetime_obj(latestRow.iloc[0][1])

    # ==================================================================================================================
    def start_update(self):
        # update day data
        date = self._getLastestDate()
        print(date)
        self._crawl_data_since_date(date)


def main():
    updater = CloseDataUpdater()
    updater.start_update()

if __name__ == '__main__':
        main()