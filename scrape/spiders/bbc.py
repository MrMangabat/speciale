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


class BBC(scrapy.Spider):
    name = 'bbc'
    # handle_httpstatus_list = [404]

    # allowed_domains = ['https://www.bbc.com/news']
    # base_url = 'https://www.bbc.com'

    def start_requests(self):
        target_feeds = [
                'https://www.bbc.com/news/science-environment-56837908', # miljø
                'https://www.bbc.com/news/world',                        # udland
                'https://www.bbc.com/news/business',            # økonomi
                'https://www.bbc.com/news/technology',                   # teknologi
                'https://www.bbc.com/news/health-65042224',              # sundhed
                'https://www.bbc.com/news/business-65124741',            # storbritannien
            ]
        try: 
            for url in target_feeds:
                print('------------------------------------------------------------------')
                print('LINK ROTATION: ', url)
                print('------------------------------------------------------------------')
                yield scrapy.Request(url = url, callback = self.parse_bbc_links) ## change callback
        except (HTTPError, URLError, ValueError):
            print('------------------------------------------------------------------')
            print('SERVER NOT FOUND!')
            print('------------------------------------------------------------------')

    def parse_bbc_links(self, response):        
        

        # print('------------------------------START-------------------------------')
        main = response.xpath('//*[@id="site-container"]')
        # print('MAIN: search_main: ',main)
        # print('MAIN DTYPE: ', type(main))
        # main = Selector(text = main)
        # print('SEARCH MAIN DTYPE: ', type(main))

        # print('------------------------------FIRST-------------------------------')
        first_part = main.xpath('//*[@id="topos-component"]//a/@href')
        # print('FIRST PART: ', (first_part))
        # print('FIRST PART DTYPE: ', type(first_part))
        # print('------------------------ACCESS <a href---------------------------------- ')
        second_part = main.xpath('//*[@role="region"]/div//a/@href')
        # print('------------------------------------------------------------------')
        # print('SECOND PART: ', (second_part))
        # print('------------------------------------------------------------------')
        third_part = main.xpath('//*[@id="lx-stream"]//a/@href')
        
        collect_links = first_part.getall() + second_part.getall() + third_part.getall()
        for href in collect_links:
            # print('------------------------------------------------------------------')
            # print('HREF: ', href)
            # print('------------------------------------------------------------------')
            yield response.follow(href, callback = self.access_bbc_articles_content)
        
        
    def access_bbc_articles_content(self, response):
        # print('-----------------------------START-------------------------------------')
        # print('--------------------------CURRENT URL-------------------------------')
        # print('CURRENT HREF: ','\n', response.url)
        # print('-------------------------SELECT TITLE----------------------------')
        article_title = response.xpath('//*[@id="main-heading"]/text()').getall()
        # print('TITLE: ','\n', article_title)
        # print('-------------------------SELECT BODY----------------------------')
        article = response.xpath('//div[@data-component="text-block"]//b/text()').getall()
        article += response.xpath('//div[@data-component="text-block"]//p/text()').getall()
        # print('BODY: ', '\n', article)
        # print('-----------------------------END-------------------------------')
        article_item = DrItem()
        article_item['article_title'] = article_title
        article_item['article_body'] = article
        article_item['suppliers_ID_unique'] = None
        article_item['published'] = None 
        article_item['tag'] = None
        article_item['link'] = response.url
        article_item['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        article_item['truth'] = None
        

#     #     #add tags according to link category
        england_regex = re.compile(r'https://www.bbc.com/news/england.*')
        science_regex = re.compile(r'https://www.bbc.com/news/science-environment.*')
        europe_regex = re.compile(r'https://www.bbc.com/news/world-europe.*')
        finance_regex = re.compile(r'https://www.bbc.com/news/business.*')
        tech_regex = re.compile(r'https://www.bbc.com/news/technology.*')
        health_regex = re.compile(r'https://www.bbc.com/news/health.*')
        politics_regex = re.compile(r'https://www.bbc.com/news/politics.*')
        politics2_regex = re.compile(r'https://www.bbc.com/news/uk-politics.*')
        
        if england_regex.match(response.url):
            article_item['tag'] = 'indland'

        if science_regex.match(response.url):
            article_item['tag'] = 'miljø'

        if europe_regex.match(response.url):
            article_item['tag'] = 'udland'

        if tech_regex.match(response.url):
            article_item['tag'] = 'teknologi'

        if finance_regex.match(response.url):
            article_item['tag'] = 'penge'

        if health_regex.match(response.url):
            article_item['tag'] = 'sundhed'

        if politics_regex.match(response.url) or politics2_regex.match(response.url):
            article_item['tag'] = 'politik'

        

        # print('-------------------------------------------------------------------')
        # print('article_title: ', article_item['article_title'])
        # print('-------------------------------------------------------------------')
        # print('article_body: ', article_item['article_body'])
        # print('-------------------------------------------------------------------')
        # print('suppliers_ID_unique: ', article_item['suppliers_ID_unique'])
        # print('-------------------------------------------------------------------')
        # print('published: ', article_item['published'])
        # print('-------------------------------------------------------------------')
        # print('link: ', article_item['link'])
        # print('-------------------------------------------------------------------')
        # print('log_time: ', article_item['log_time'])
        # print('-------------------------------------------------------------------')
        # print('tag: ', article_item['tag'])
        # print('-------------------------------------------------------------------')

        yield article_item