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

class BBCRSS(scrapy.Spider):
    name = 'bbcrss'
    
    def start_requests(self):
        target_feeds = [
            'http://feeds.bbci.co.uk/news/world/europe/rss.xml',
            'http://feeds.bbci.co.uk/news/england/rss.xml',
            'http://feeds.bbci.co.uk/news/rss.xml',
            'http://feeds.bbci.co.uk/news/uk/rss.xml',
            'http://feeds.bbci.co.uk/news/business/rss.xml',
            'http://feeds.bbci.co.uk/news/politics/rss.xml',
            'http://feeds.bbci.co.uk/news/health/rss.xml',
            'http://feeds.bbci.co.uk/news/education/rss.xml',
            'http://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
            'http://feeds.bbci.co.uk/news/technology/rss.xml',
            'http://feeds.bbci.co.uk/news/rss.xml'
        ]

        try: 
            for url in target_feeds:
                yield scrapy.Request(url = url, callback = self.parse)
        except (HTTPError, URLError):
            print('The server could not be found!')

    def parse(self, response):
        rss_feed = response.xpath('//item')
        
        for index, feed in enumerate(rss_feed):
            item = DrItem()
            # //item[1]/title | //item[1]/link | //item[1]/guid | //item[1]/pubDate
            item['article_title'] = response.xpath('//item[$i]/title/text()', i = index + 1).get()
            item['published']     = response.xpath('//item[$i]/pubDate/text()', i = index + 1).get()
            item['id']            = response.xpath('//item[$i]/guid/text()', i = index + 1).get()
            item['link']          = response.xpath('//item[$i]/link/text()', i = index + 1).get()

            # print('---------------------------------------------------------------------------------')
            # print('ITEMS: ','\n', item)
            # print('---------------------------------------------------------------------------------')

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
        # article = response.xpath('//div[@data-component="text-block"]//p/text()').getall() #xpath('//*[@id="main-content"]/article')
        # print('---------------------------------------------------------------------------------')
        # print('ARTICLE: ','\n',type(article),'\n', article)
        # print('---------------------------------------------------------------------------------')
        article_item = DrItem()
        article_item['article_title'] = article_title
        article_item['article_body'] = response.xpath('//div[@data-component="text-block"]//p/text()').getall()
        article_item['published'] = published
        article_item['suppliers_ID_unique'] = id
        article_item['link'] = link
        article_item['tag'] = None
        article_item['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # england_regex = re.compile(r'https://www.bbc.com/news/england.*')
        # science_regex = re.compile(r'https://www.bbc.com/news/science-environment.*')
        # europe_regex = re.compile(r'https://www.bbc.com/news/world-europe-.*')
        # finance_regex = re.compile(r'https://www.bbc.com/news/business.*')
        # tech_regex = re.compile(r'https://www.bbc.com/news/technology.*')
        # health_regex = re.compile(r'https://www.bbc.com/news/health.*')
        # politics_regex = re.compile(r'https://www.bbc.com/news/politics.*')
        # politics2_regex = re.compile(r'https://www.bbc.com/news/uk-politics.*')
        england_regex = re.compile(r'https://www.bbc.co.uk/news/england.*')
        uk_regex = re.compile(r'https://www.bbc.co.uk/news/uk.*')
        science_regex = re.compile(r'https://www.bbc.co.uk/news/science-environment.*')
        europe_regex = re.compile(r'https://www.bbc.co.uk/news/world-europe.*')
        finance_regex = re.compile(r'https://www.bbc.co.uk/news/business.*')
        tech_regex = re.compile(r'https://www.bbc.co.uk/news/technology.*')
        health_regex = re.compile(r'https://www.bbc.co.uk/news/health.*')
        politics_regex = re.compile(r'https://www.bbc.co.uk/news/politics.*')
        politics2_regex = re.compile(r'https://www.bbc.co.uk/news/uk-politics.*')

        if england_regex.match(article_item['link']) or uk_regex.match(article_item['link']):
            article_item['tag'] = 'indland'

        if science_regex.match(article_item['link']):
            article_item['tag'] = 'miljø'

        if europe_regex.match(article_item['link']):
            article_item['tag'] = 'udland'

        if tech_regex.match(article_item['link']):
            article_item['tag'] = 'teknologi'

        if finance_regex.match(article_item['link']):
            article_item['tag'] = 'penge'

        if health_regex.match(article_item['link']):
            article_item['tag'] = 'sundhed'

        if politics_regex.match(article_item['link']) or politics2_regex.match(article_item['link']):
            article_item['tag'] = 'politik'

        yield article_item
