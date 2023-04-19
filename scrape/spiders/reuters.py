

# 

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
    name = 'reuters'
    allowed_domains = ['reuters.com']
    
    def start_requests(self):
        target_feeds = [
            # udland
            'https://www.reuters.com/world/europe/',
            'https://www.reuters.com/world/reuters-next/',
            # penge
            'https://www.reuters.com/business/',
            'https://www.reuters.com/business/cop/',
            'https://www.reuters.com/business/autos-transportation/',
            'https://www.reuters.com/business/energy/',
            'https://www.reuters.com/business/environment/',
            'https://www.reuters.com/business/finance/',
            'https://www.reuters.com/business/healthcare-pharmaceuticals/',
            'https://www.reuters.com/business/retail-consumer/',
            'https://www.reuters.com/business/sustainable-business/',
            'https://www.reuters.com/business/charged/',
            'https://www.reuters.com/business/future-of-health/',
            'https://www.reuters.com/business/future-of-money/',
            'https://www.reuters.com/business/take-five/',
            'https://www.reuters.com/business/reuters-impact/',
            'https://www.reuters.com/markets/deals/',
            'https://www.reuters.com/markets/stocks/europe/',
            'https://www.reuters.com/markets/wealth/',
            # teknology
            'https://www.reuters.com/technology/',
            'https://www.reuters.com/technology/',
            'https://www.reuters.com/technology/reuters-momentum/',
            ]
        
        try: 
            for url in target_feeds:
                yield scrapy.Request(url = url , callback = self.parse)
        except (HTTPError, URLError):
            print('The server could not be found!')

    def parse(self, response):
        navigation_bar = response.xpath('//*[@id="main-content"]//a/@href').getall()
        for href in navigation_bar:
            yield response.follow(url = href, callback = self.parse_links)

    def parse_links(self, response):
        article_title = response.xpath('//h1/text()').getall()
        article_body = response.xpath('//*[@id="main-content"]/article/div[1]/div[2]/div/div//div//p/text()').getall()
                                      #//*[@id="main-content"]/article/div[1]/div[2]/div/div/div
                                      #//*[@id="main-content"]/article/div[1]/div[2]/div/div/div/div[1]
        published = response.xpath('//*[@id="main-content"]/article/div[1]/div[2]/header/div/div/time/span[2]/text()').getall()
        article_item = DrItem()

        print('----------------------------------------------NEW ARTICLE----------------------------------------')
        article_item['article_title'] = article_title
        article_item['article_body'] = article_body
        article_item['suppliers_ID_unique'] = None
        article_item['published'] = published
        article_item['tag'] = None
        article_item['link'] = response.url
        article_item['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        article_item['truth'] = None

    #     # add tags according to link category
    #     # Define regular expressions and tags as key-value pairs in a dictionary
        regex_dict = {
            
            # udland
            r'https://www.reuters.com/world/europe/'                        :'udland',
            r'https://www.reuters.com/world/reuters-next/'                  :'udland',
            # penge
            r'https://www.reuters.com/business/'                            :'penge',          
            r'https://www.reuters.com/business/cop/'                        :'penge',
            r'https://www.reuters.com/business/autos-transportation/'       :'penge',
            r'https://www.reuters.com/business/energy/'                     :'penge',
            r'https://www.reuters.com/business/future-of-money/'            :'penge',
            r'https://www.reuters.com/business/take-five/'                  :'penge',
            r'https://www.reuters.com/business/reuters-impact/'             :'penge',
            r'https://www.reuters.com/markets/deals/'                       :'penge',
            r'https://www.reuters.com/markets/stocks/europe/'               :'penge',
            r'https://www.reuters.com/markets/wealth/'                      :'penge',
            r'https://www.reuters.com/business/finance/'                    :'health',
            r'https://www.reuters.com/business/healthcare-pharmaceuticals/' :'health',
            r'https://www.reuters.com/business/retail-consumer/'            :'penge',
            r'https://www.reuters.com/business/sustainable-business/'       :'penge',
            r'https://www.reuters.com/business/charged/'                    :'penge',
            r'https://www.reuters.com/business/future-of-health/'           :'health',
            r'https://www.reuters.com/business/environment/'                :'miljø',
            # teknology
            r'https://www.reuters.com/technology/'                          :'teknoogi',
            r'https://www.reuters.com/technology/reuters-momentum/'         :'teknoogi',
            
        }

        # Loop through the dictionary and check for matches
        for regex_pattern, tag in regex_dict.items():
            if re.compile(regex_pattern).match(response.url):
                article_item['tag'] = tag

        print('-------------------------------------------------------------------')
        print('article_title: ', '\n', article_item['article_title'])
        print('-------------------------------------------------------------------')
        print('article_body: ', '\n', article_item['article_body'])
        print('-------------------------------------------------------------------')
        print('suppliers_ID_unique: ', '\n', article_item['suppliers_ID_unique'])
        print('-------------------------------------------------------------------')
        print('published: ', '\n', article_item['published'])
        print('-------------------------------------------------------------------')
        print('link: ', '\n', article_item['link'])
        print('-------------------------------------------------------------------')
        print('log_time: ', '\n', article_item['log_time'])
        print('-------------------------------------------------------------------')
        print('tag: ', '\n', article_item['tag'])
        print('-------------------------------------------------------------------')
        
        yield article_item