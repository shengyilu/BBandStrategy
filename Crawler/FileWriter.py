# -*- coding: UTF-8 -*-

import os
import csv
from Crawler import Const

class FileWriter():
    def __init__(self):
        ''' Make directory if not exist when initialize '''
        self._init_data_folder()

    def _init_data_folder(self):
        # create root data folder if not exists
        if not os.path.isdir(Const.STOCK_DATA_FOLDER_NAME):
            os.mkdir(Const.STOCK_DATA_FOLDER_NAME)

        # create history folder under data folder if not exists
        if not os.path.isdir(Const.STOCK_HISTORY_FOLDER_PATH):
            os.mkdir(Const.STOCK_HISTORY_FOLDER_PATH)

    def record_stock_data(self, file_name, row):
        ''' Save row to csv file '''
        f = open(file_name, 'a')
        cw = csv.writer(f, lineterminator='\n')
        cw.writerow(row)
        f.close()

    def record_stock_datas(self, file_name, rows):
        ''' Save row to csv file '''
        f = open(file_name, 'a')
        cw = csv.writer(f, lineterminator='\n')
        cw.writerows(rows)
        f.close()


    def record_stock_list(self, file_name, stock_list):
        ''' Save stock list as csv file '''
        f = open(file_name, 'w')

        cw = csv.writer(f, lineterminator='\n')
        for stock in stock_list:
            #print(stock)
            stock_id_name_pair = stock.split(" ")
            cw.writerow(stock_id_name_pair)
        f.close()

