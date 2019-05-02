import pandas as pd
import requests
from Crawler import *


class StockShareCapitalCrawler():
    SHARE_CAPITAL_URL = 'https://stock.wespai.com/p/28904'

    def __init__(self):
        ''' Make directory if not exist when initialize '''
        self._file_writer = FileWriter()

    def _parseShareCapital(self):
        headers = requests.utils.default_headers()
        headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
            }
        )
        response = requests.get(StockShareCapitalCrawler.SHARE_CAPITAL_URL, headers=headers)

        df = pd.read_html(response.text)[0]
        df = df[['代號', '公司', '資本額(億)']]
        df.to_csv('../data/ShareCapital.csv', index=False)






def main():
    crawler = StockShareCapitalCrawler()
    crawler._parseShareCapital()

if __name__ == '__main__':
    main()