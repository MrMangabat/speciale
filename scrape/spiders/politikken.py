
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


økonomi = 'https://wallnot.dk/?m=politiken'

class Politikken(scrapy.Spider):
    name = 'politikken'

    def start_requests(self):
        target_feeds = [
            økonomi,
            ]
        try: 
            for url in target_feeds:
                print(url)
                yield scrapy.Request(url = url, callback = self.parse)
        except (HTTPError, URLError):
            print('The server could not be found!')

    def parse(self, response):
        # Extract all articles
        all_articles = response.xpath("//p[@class='article']").getall()

        # Extract links from each article
        for index, article in enumerate(all_articles):
            item = DrItem()
            ###### Same for all articles coming from wallnot.dk
            article_selector = Selector(text = article)
            access_class_art = article_selector.xpath('//*[@class="art"]')
            access_link = Selector(text = access_class_art.get())
            
            title = access_class_art.xpath('.//a/text()').get()
            some_id = article_selector.css('span::attr(id)').extract_first()
            link = access_link.xpath('.//a/@href').get()
            ###### Same for all articles coming from wallnot.dk
            item['article_title']   = title         # lever        
            item['suppliers_ID_unique'] = some_id   # lever
            item['link']            = link          # lever          
 
            article_body = scrapy.Request(
                url = item['link'],
                callback = self.parse_article_body,
                cb_kwargs = {
                    'article_title': item['article_title'],
                    'id': item['suppliers_ID_unique'], 
                    'link': item['link'],
                    }
                )
        
            yield article_body

    def parse_article_body(self, response, article_title, id, link):       
        article = response.xpath("//div[contains(@class, 'article__body')]").getall()

        for body in article:
            article_item = DrItem()
            # print('------------------------INSIDE FOR LOOP POLITIKKEN------------------------------')
            body_selector = Selector(text = body)
            #extract article body
            access_body = body_selector.xpath('//p[contains(@class, "body__p")]/text()').getall() # dtype = list
            
            article_item['article_title'] = article_title
            article_item['article_body'] = access_body
            article_item['suppliers_ID_unique'] = id
            article_item['published'] = None 
            article_item['tag'] = None
            article_item['link'] = link
            article_item['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        #add tags according to link category
        penge_regex = re.compile(r'https://politiken.dk/oekonomi/.*')
        politik_regex = re.compile(r'https://politiken.dk/politik/.*')
        indland_regex = re.compile(r'https://politiken.dk/indland/.*')
        udland_regex = re.compile(r'https://politiken.dk/udland/.*')
        
        if penge_regex.match(link):
            article_item['tag'] = 'økonomi'
        
        if politik_regex.match(link):
            article_item['tag'] = 'politik'
        
        if udland_regex.match(link):
            article_item['tag'] = 'udland'

        if indland_regex.match(link):
            article_item['tag'] = 'indland'
        
        yield article_item