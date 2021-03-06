import sys
import csv
from Crawler import Const
import os
import io
import sys
import importlib

class StockListProvider():

    def __init__(self):
        importlib.reload(sys)
        self._stock_list_csv_path = '{}/{}'.format(Const.STOCK_DATA_FOLDER_NAME, Const.STOCK_LIST_FILE_NAME)
        self._stock_dict = {}
        self._init_dict()

    def _init_dict(self):
        if not os.path.isfile(self._stock_list_csv_path):
            return None

        file = io.open(self._stock_list_csv_path, 'r', encoding='utf-8')
        csv_cursor = csv.reader(file)
        for row in csv_cursor:
            self._stock_dict[row[0]] = row[1]

    def stock_id_exists(self, id):
        if id in self._stock_dict:
            if not id in Const.STOCK_IGNORE_LIST:
                return True
        else:
            return False

    def get_stock_id_list(self):
        return self._stock_dict.keys()

#
# def main():
#     provider = StockListProvider()
#
# if __name__ == '__main__':
#         main()