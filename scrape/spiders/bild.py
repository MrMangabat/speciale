
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



class Bild(scrapy.Spider):
    name = 'bild'
    allowed_domains = ['bild.de']
    def start_requests(self):
        target_feeds = [
            #politik - navbar
            'https://m.bild.de/news/inland/news-inland/home-15665814.bildMobile.html?t_ref=https:/www.bild.de/politik/inland/politik-inland/werbeverbot-betrifft-auch-oster-suessigkeiten-schoko-aufstand-gegen-oezdemir-83464270.bild.html'
            'https://www.bild.de/politik/ausland/politik-ausland/home-15683414.bild.html',
            'https://m.bild.de/home/hot-on-bild/bild-kommentar/kommentare-meinungen-und-kolumnen-zu-aktuellen-themen-35874522.bildMobile.html?t_ref=https:/www.bild.de/home/hot-on-bild/bild-kommentar/kommentare-meinungen-und-kolumnen-zu-aktuellen-themen-35874522.bild.html',
            #news - navbar
            'https://www.bild.de/news/startseite/news/news-16804530.bild.html?t_ref=https:/m.bild.de/politik/ausland/politik-ausland/home-15683414.bildMobile.html?t_ref=https:/www.bild.de/bild-plus/auto/tests/tests/suv-gebraucht-kaufen-7-kauftipps-mit-bester-langzeit-qualitaet-83442668.bild.html?t_ref=https:/m.bild.de/bild-plus/auto/tests/tests/suv-gebraucht-kaufen-7-kauftipps-mit-bester-langzeit-qualitaet-83442668.bildMobile.html',
            'https://www.bild.de/news/inland/news-inland/home-15665814.bild.html',
            'https://www.bild.de/news/ausland/news-ausland/home-15681774.bild.html',
            'https://www.bild.de/news/leserreporter/leserreporter/home-15682146.bild.html',
            #counselor - navbar
            'https://www.bild.de/ratgeber/gesundheit/gesundheit/home-15734752.bild.html',
            'https://www.bild.de/geld/mein-geld/mein-geld/mein-geld-46332734.bild.html',
            'https://m.bild.de/geld/startseite/geld/geld-15683376.bildMobile.html'
            ]
        try: 
            for url in target_feeds:
                print(url)
                yield scrapy.Request(url = url, callback = self.parse)
        except (HTTPError, URLError):
            print('The server could not be found!')

    def parse(self, response):

        all_links = response.xpath('//article[@data-teaser-position]/a/@href').getall()
        # print('all_links: ', all_links)
        for href in all_links:
            yield response.follow(url = href, callback = self.access_articles)        
        
    def access_articles(self, response):             
        article_item = DrItem()

        article_body_div_1 = response.xpath('//*[@id="__layout"]/div/div/div[2]/main/article//div//p/text()').getall() # giver nogle
        # cleaning the article body
        remove_signs = ['\xa0', '\n', '<\i>', '<i>']
        for i in range(len(article_body_div_1)):
            for sign in remove_signs:
                article_body_div_1[i] = article_body_div_1[i].replace(sign, '')

        # cleaning for suppliers unique id
        published = response.xpath('//*[@id="__layout"]/div/div/div[2]/main/article/time/text()').get()
        published = published.replace('\n', '')

        article_item['article_title'] = response.xpath('//*[@id="__layout"]/div/div/div[2]/main/article/h1/span[3]/text()').get()
        article_item['article_body'] = article_body_div_1
        article_item['suppliers_ID_unique'] = None
        article_item['published'] = published
        article_item['tag'] = None
        article_item['link'] = response.url
        article_item['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        article_item['truth'] = None

        # print('-------------------------------------------------------------------')
        # print('article_title: ', '\n', article_item['article_title'])
        # print('-------------------------------------------------------------------')
        # print('article_body: ', '\n', article_item['article_body'])
        # print('-------------------------------------------------------------------')
        # print('suppliers_ID_unique: ', '\n', article_item['suppliers_ID_unique'])
        # print('-------------------------------------------------------------------')
        # print('published: ', '\n', article_item['published'])
        # print('-------------------------------------------------------------------')
        # print('link: ', '\n', article_item['link'])
        # print('-------------------------------------------------------------------')
        # print('log_time: ', '\n', article_item['log_time'])
        # print('-------------------------------------------------------------------')
        # print('tag: ', '\n', article_item['tag'])
        # print('-------------------------------------------------------------------')

    #     #add tags according to link category
        indland_regex = re.compile(r'https://www.bild.de/politik/inland/.*')         
        indland_regex = re.compile(r'https://www.bild.de/regional/.*') 
        international_politics_regex = re.compile(r'https://www.bild.de/politik/ausland/.*')
        penge_regex = re.compile(r'https://www.bild.de/geld/.*') 
        health_regex = re.compile(r'https://www.bild.de/ratgeber/gesundheit/.*')
        
        if penge_regex.match(response.url):
            article_item['tag'] = 'penge'
        
        if health_regex.match(response.url):
            article_item['tag'] = 'health'
        
        if international_politics_regex.match(response.url):
            article_item['tag'] = 'udland'

        if indland_regex.match(response.url):
            article_item['tag'] = 'indland'

        if indland_regex.match(response.url):
            article_item['tag'] = 'politik'
        
        yield article_item