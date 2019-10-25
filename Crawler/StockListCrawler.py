import requests
import re
from lxml import etree
from Crawler import Const

class StockListCrawler():

    TSE_STOCK_LIST = 'https://tw.stock.yahoo.com/h/kimosel.php'
    TSE_STOCK_CATEGORY = 'https://tw.stock.yahoo.com/h/kimosel.php?tse={CAT_INDEX}&cat=%C2d%A5b%BE%C9&form=menu&form_id=stock_id&form_name=stock_name&domain=0'
    CATEGORY_TSE_INDEX = 1
    CATEGORY_OTC_INDEX = 2
    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'
    REQUEST_HEADER = { 'User-Agent': USER_AGENT }

    def __init__(self):
        ''' Make directory if not exist when initialize '''

    def _fetch_stock_category(self, category_index):
        url = StockListCrawler.TSE_STOCK_CATEGORY.format(CAT_INDEX=category_index)
        page = requests.get(url, headers=StockListCrawler.REQUEST_HEADER)
        page.encoding = 'big5'
        root = etree.HTML(page.text)

        return root.xpath('//tr/td/a/text()')

    def _fetch_stock_list(self):
        stock_list = []

        stock_category_indexes = [StockListCrawler.CATEGORY_TSE_INDEX,
                                  StockListCrawler.CATEGORY_OTC_INDEX]

        count = 0
        for category_index in stock_category_indexes:
            categories_list = self._fetch_stock_category(category_index)
            for category in categories_list:
                print(category)
                query_params = {
                    'tse': category_index,
                    'cat': category
                }
                page = requests.get(StockListCrawler.TSE_STOCK_LIST, params=query_params, headers=StockListCrawler.REQUEST_HEADER)
                page.encoding = 'big5'
                root = etree.HTML(page.text)
                if not root == None:
                    stock_id_name_list = root.xpath('//form[@name="stock"]//td/a/text()')
                    for stock_id_name in stock_id_name_list:
                        stock_id_name = stock_id_name.replace("\n", "")
                        id = stock_id_name.split(" ")[0]
                        if len(id) <= 4 and id.isdigit() and not id in Const.STOCK_IGNORE_LIST:
                            stock_list.append(stock_id_name)
                            count += 1

        return self._clean_row(stock_list)

    def _clean_row(self, row):
        ''' Clean comma and spaces '''
        for index, content in enumerate(row):
            row[index] = re.sub(",", "", content.strip())
        return row

    def fetch_stock_list(self):
        stock_list = self._fetch_stock_list()
        return stock_list

#
def main():
    crawler = StockListCrawler()
    crawler.fetch_stock_list()


if __name__ == '__main__':
    main()