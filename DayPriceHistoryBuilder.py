from Crawler import *
from Crawler import Const
import os
import shutil
from datetime import datetime, timedelta
import csv
import time

class DayPriceHistoryBuilder():
    def __init__(self, is_keep_old=False):
        self._file_writer = FileWriter()
        self._crawler = StockPriceCrawler()
        self._stock_list_provider = StockListProvider()

        if not is_keep_old:
            self._remove_old_data(Const.STOCK_HISTORY_FOLDER_PATH)

        self._init_data_folder()

    def _remove_old_data(self, file_name):
        if os.path.isdir(file_name):
            shutil.rmtree(file_name)

        if os.path.isfile(file_name):
            os.remove(file_name)

    def _init_data_folder(self):
        # create root data folder if not exists
        if not os.path.isdir(Const.STOCK_DATA_FOLDER_NAME):
            os.mkdir(Const.STOCK_DATA_FOLDER_NAME)

        # create history folder under data folder if not exists
        if not os.path.isdir(Const.STOCK_HISTORY_FOLDER_PATH):
            os.mkdir(Const.STOCK_HISTORY_FOLDER_PATH)

    # =============================================================================================================
    # Step 1: Crawl data
    def _crawl_data_days(self, days):
        '''
        Crawl history price data by days
        :param days: days backward from today
        :return: None
        '''
        days_before = days
        while days_before >= 0:
            query_date = datetime.today() - timedelta(days=days_before)
            print(query_date)
            time.sleep(4)
            stock_day_data_dict = self._crawler.fetch_data(query_date)
            self._save_data(stock_day_data_dict)
            days_before -= 1


    def _save_data(self, stock_data_dict):
        print('_save_data')
        stock_list = self._stock_list_provider.get_stock_id_list()
        for stock_id in stock_list:
            if stock_id in stock_data_dict:
                row = stock_data_dict[stock_id]
                file_path = '{}/{}-raw.csv'.format(Const.STOCK_HISTORY_FOLDER_PATH, stock_id)
                self._file_writer.record_stock_data(file_path, row)

    # =============================================================================================================
    def build_history(self, days):
        # Step 1
        self._crawl_data_days(days)


def main():
    builder = DayPriceHistoryBuilder(is_keep_old=False)
    builder.build_history(200)

if __name__ == '__main__':
    main()