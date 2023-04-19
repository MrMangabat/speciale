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
    name = 'thesun'
    base_url = 'https://www.the-sun.com'

    def start_requests(self):
        target_feeds = [
            'https://www.thesun.co.uk/money/news-money/',
            'https://www.thesun.co.uk/money/business/',
            'https://www.the-sun.com/news/uk-news/',
            'https://www.the-sun.com/news/world-news/',
            'https://www.the-sun.com/health/',
            'https://www.the-sun.com/tech/news-tech/',
            ''
        ]
        try: 
            for url in target_feeds:
                yield scrapy.Request(url = url, callback = self.parse)
        except (HTTPError, URLError):
            print('The server could not be found!')

    def parse(self, response):
        # getting all current hrefs from the main-content xpath
        overview_links = response.xpath('//div[@class="sun-row teaser"]//a/@href').getall()              
        
        # Remove links containing "/page" from the overview_links list
        overview_links = [href for href in overview_links if "/page" not in href]

        # Iterate through the links in the overview_links list
        for i in range(len(overview_links)):
            href = overview_links[i]
        # If the link starts with "/", add "https://www.the-sun.com" in front
            if href.startswith("/"):
                overview_links[i] = self.base_url + href

                yield scrapy.Request(url = overview_links[i], callback = self.parse_links)
        
        # getting all pages from with article
        next_page = response.xpath('//a[@rel="next"]/@href').getall()
        for i in range(len(next_page)):
            href = next_page[i]

            # If the link starts with "/", add "https://www.the-sun.com" in front
            if href.startswith("/"):
                next_page[i] = self.base_url + href

                yield scrapy.Request(url = next_page[i], callback = self.parse)           
    
    def parse_links(self, response):
        # accessing all articles from main-content xpath
        article_item = DrItem()
        article_title = response.xpath('//h1[@class="article__headline"]/text()').getall()
        
        article_body = response.xpath('//*[@id="main-content"]/section/div/div[1]/article/div[2]/div[2]//p/text()').getall()

        published = response.xpath('//*[@id="main-content"]/section/div/div[1]/article/div[1]/div[2]/div/div/ul/li[1]/time/span[2]/text()').getall()
        # for text_body in article:
        article_item['article_title'] = article_title
        article_item['article_body'] = article_body
        article_item['published'] = published
        article_item['suppliers_ID_unique'] = None
        article_item['link'] = response.url
        article_item['tag'] = None
        article_item['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        local_regex = re.compile(r'https://www.the-sun.com/news/.*')
        world_regex = re.compile(r'https://www.the-sun.com/news/world-news.*')
        business_regex = re.compile(r'https://www.thesun.co.uk/money/.*')
        technology_regex = re.compile(r'https://www.the-sun.com/tech/.*')
        helth_regex = re.compile(r'https://www.the-sun.com/health/.*')

        if world_regex.match(response.url):
            article_item['tag'] = 'udland'
        
        elif business_regex.match(response.url):
            article_item['tag'] = 'penge'

        elif local_regex.match(response.url):
            article_item['tag'] = 'indland'

        elif technology_regex.match(response.url):
            article_item['tag'] = 'teknologi'

        elif helth_regex.match(response.url):
            article_item['tag'] = 'sundhed'

        yield article_item
