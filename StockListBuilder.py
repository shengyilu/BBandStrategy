from Crawler import *
from Crawler import Const
import os
import shutil
import logging
from datetime import datetime, timedelta

class StockListBuilder():
    def __init__(self):
        self._file_writer = FileWriter()
        self._crawler = StockListCrawler()

    def _remove_old_data(self, file_name):
        if os.path.isdir(file_name):
            shutil.rmtree(file_name)

        if os.path.isfile(file_name):
            os.remove(file_name)

    def build_stock_list(self):
        '''
        Fetch all stock_id from Yahoo and save it as .csv file in /data/StockList_Taiwan.csv
        :return: None
        '''
        file_name = "{0}/{1}".format(Const.STOCK_DATA_FOLDER_NAME, Const.STOCK_LIST_FILE_NAME)
        self._remove_old_data(file_name)
        stock_list = self._crawler.fetch_stock_list()
        self._file_writer.record_stock_list(file_name, stock_list)


def main():
    builder = StockListBuilder()
    builder.build_stock_list()
    provider = StockListProvider()
    #print(provider.get_stock_id_list())


if __name__ == '__main__':
    main()