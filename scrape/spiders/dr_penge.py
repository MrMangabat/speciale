
import re
import sys

import scrapy
from scrapy.exceptions import DropItem
from datetime import datetime
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


class DrPenge(scrapy.Spider):
    name = 'drpenge'

    def start_requests(self):
        target_feeds = [
            # 'https://www.dr.dk/nyheder/service/feeds/indland',
            # 'https://www.dr.dk/nyheder/service/feeds/udland',
            # 'https://www.dr.dk/nyheder/service/feeds/politik',
            'https://www.dr.dk/nyheder/service/feeds/penge']
        try: 
            for url in target_feeds:
                print(url)
                yield scrapy.Request(url = url, callback = self.parse)
        except (HTTPError, URLError):
            print('The server could not be found!')

    def parse(self, response):
        rss_feed = response.xpath('//item/guid').getall()

        for index, feed in enumerate(rss_feed):
            item = DrItem()
# //item[1]/title | //item[1]/link | //item[1]/guid | //item[1]/pubDate
            item['article_title']   = response.xpath('//item[$i]/title/text()', i = index + 1).get()
            item['published']       = response.xpath('//item[$i]/pubDate/text()', i = index + 1).get()           
            item['id']              = response.xpath('//item[$i]/guid/text()', i = index + 1).get()
            item['link']            = response.xpath('//item[$i]/link/text()', i = index + 1).get()

            
            article_body = scrapy.Request(
                url = item['link'],
                callback = self.parse_article_body,
                cb_kwargs = {
                    'article_title': item['article_title'],
                    'published': item['published'],
                    'id': item['id'], 
                    'link': item['link'],
                    }
                )
            yield article_body

    def parse_article_body(self, response, article_title, published, id, link):
        article = response.css('article')
        article_item = DrItem()
  
        for text_body in article:
            # print('------------------------INSIDE FOR LOOP DRPENGE------------------------------')

            article_item['article_title'] = article_title
            article_item['article_body'] = text_body.css('p.dre-article-body-paragraph.dre-variables::text').getall()
            article_item['published'] = published
            article_item['suppliers_ID_unique'] = id
            article_item['link'] = link
            article_item['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #     # Setting tags for each article
        penge_regex = re.compile(r'https://www.dr.dk/nyheder/penge/.*')

        if penge_regex.match(link):
            article_item['tag'] = 'penge'
        else:
            article_item['tag'] = None

        yield article_item