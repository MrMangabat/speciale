

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

class TheSun(scrapy.Spider):
    name = 'financialtimes'
    def start_requests(self):
        target_feeds = [
            'https://www.ft.com/myft/following/9fc9d085-15cc-4a6a-af91-0745f34a0da6.rss'
            
        ]
        try: 
            for url in target_feeds:
                yield scrapy.Request(url = url, callback = self.parse)
        except (HTTPError, URLError):
            print('The server could not be found!')

    def parse(self, response):
        rss_feed = response.xpath('//item')
        print('RSS FEED: ', rss_feed)
    #     for index, feed in enumerate(rss_feed):
    #         item = DrItem()
    #         # //item[1]/title | //item[1]/link | //item[1]/guid | //item[1]/pubDate
    #         item['article_title'] = response.xpath('//item[$i]/title/text()', i = index + 1).get()
    #         item['published']     = response.xpath('//item[$i]/pubDate/text()', i = index + 1).get()
    #         item['id']            = response.xpath('//item[$i]/guid/text()', i = index + 1).get()
    #         item['link']          = response.xpath('//item[$i]/link/text()', i = index + 1).get()

    #         # print('---------------------------------------------------------------------------------')
    #         # print('ITEMS: ','\n', item)
    #         # print('---------------------------------------------------------------------------------')

    #         article_body = scrapy.Request(
    #             url = item['link'],
    #             callback = self.parse_article_body,
    #             cb_kwargs = {
    #                 'article_title': item['article_title'],
    #                 'published': item['published'],
    #                 'id': item['id'],
    #                 'link': item['link'],
    #                 }
    #             )
    #         yield article_body

    # def parse_article_body(self, response, article_title, published, id, link):
    #     article = response.css('article')
    #     article_item = DrItem()
    #     for text_body in article:
    #         article_item['article_title'] = article_title
    #         article_item['article_body'] = text_body.xpath('//*[@id="row01col02"]/div[3]/div/div/div[6]/div/p/text()').getall()
    #         article_item['published'] = published
    #         article_item['suppliers_ID_unique'] = id
    #         article_item['link'] = link
    #         article_item['tag'] = None
    #         article_item['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    #     print('---------------------------------------------------------------------------------')
    #     print('ARTICLE ITEM: ','\n', article_item['link'])