


#utils
from datetime import datetime
import re
import sys
# Scrapy
import scrapy
from scrapy.selector import SelectorList, Selector
from scrapy.exceptions import DropItem

# imports item from the dr_article_spider.py file
from analysisSpider.items import DrItem
from analysisSpider.itemloaders import DrItemLoader
from data_generator.utils.utility import get_root_path
from data_generator.utils.sql_utils import get_database_engine
from data_generator.database.tables import Logs
from data_generator.database.datawriter import DataWriter
## errors
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
sys.path.append('..')



class Reuters(scrapy.Spider):
    name = 'bankofuk'
    allowed_domains = ['bankofengland.co.uk']
    
    def start_requests(self):
        target_feeds = [
            'https://www.bankofengland.co.uk/rss/publications',
            'https://www.bankofengland.co.uk/rss/statistics',
            'https://www.bankofengland.co.uk/rss/news',
            'https://www.bankofengland.co.uk/rss/prudential-regulation-publications',


        ]
        
        try: 
            for url in target_feeds:
                yield scrapy.Request(url = url , callback = self.parse)
        except (HTTPError, URLError):
            print('The server could not be found!')

    def parse(self, response):
        navigation_bar = response.xpath('//item').getall()
        for i in navigation_bar:
            print(i, '\n')
        # print('TEST: ',navigation_bar)
        # for href in navigation_bar:
        #     yield response.follow(url = href, callback = self.parse_links)