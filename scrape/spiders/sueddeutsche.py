

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



class SuedDeutsche(scrapy.Spider):
    name = 'sued'
    allowed_domains = ['sueddeutsche.de']
    
    def start_requests(self):
        target_feeds = [
            #politik - navbar
            'https://www.sueddeutsche.de',
            'https://www.sueddeutsche.de/thema/Energie',
            'https://www.sueddeutsche.de/thema/Energiepolitik',
            'https://www.sueddeutsche.de/thema/Erneuerbare_Energien',
            'https://www.sueddeutsche.de/thema/Atomkraft',
            'https://www.sueddeutsche.de/thema/Erdgas',
            'https://www.sueddeutsche.de/thema/Fl%C3%BCssiggas',
            'https://www.sueddeutsche.de/thema/Erd%C3%B6l',
            'https://www.sueddeutsche.de/thema/Windkraft',
            'https://www.sueddeutsche.de/thema/Energie_sparen',
            'https://www.sueddeutsche.de/thema/Braunkohle',
            'https://www.sueddeutsche.de/thema/Geldanlage',
            'https://www.sueddeutsche.de/thema/Reden_wir_%C3%BCber_Geld',
            'https://www.sueddeutsche.de/thema/Wirtschaftspolitik',
            'https://www.sueddeutsche.de/thema/Banken_und_Finanzindustrie',
            'https://www.sueddeutsche.de/thema/Deutschland',
            'https://www.sueddeutsche.de/thema/Wirtschaftspolitik',
            ]
        try: 
            for url in target_feeds:
                if url == 'https://www.sueddeutsche.de':
                    yield scrapy.Request(url = url , callback = self.landing_page)
                else:
                    yield scrapy.Request(url = url, callback = self.theme_pages)
                yield scrapy.Request(url = url , callback = self.landing_page)
        except (HTTPError, URLError):
            print('The server could not be found!')


    def theme_pages(self, response):
        articles = response.xpath('//article[@data-manual]//a/@href').getall()

        for href in articles:
               yield response.follow(url = href, callback = self.parse_links)

    def landing_page(self, response):
        navigation_bar = response.xpath('//*[@id="header-navigation"]/div[2]/div/div[2]/nav/ul//a/@href').getall()
    
        removed_navigation_links = [
            'https://www.sueddeutsche.de/meinesz',
            'https://plus.sueddeutsche.de',
            'https://www.sueddeutsche.de/thema/Ukraine',
            'https://www.sueddeutsche.de/panorama',
            'https://www.sueddeutsche.de/sport',
            'https://www.sueddeutsche.de/muenchen',
            'https://www.sueddeutsche.de/kultur',
            'https://www.sueddeutsche.de/bayern',
            'https://www.sueddeutsche.de/leben',
            'https://www.sueddeutsche.de/stil',
            'https://www.sueddeutsche.de/karriere',
            'https://www.sueddeutsche.de/reise',
            'https://www.sueddeutsche.de/auto'
        ]

        navigation_bar_copy = navigation_bar[:]  # Create a copy of navigation_bar to avoid modifying original list while iterating
        for href in navigation_bar_copy:
            if href in removed_navigation_links:
                navigation_bar.remove(href)  #
        
        for href in navigation_bar:
            yield response.follow(url = href, callback = self.topic_to_article)
        
        top_teasers = response.xpath('/html/body/div[4]/main//section//a/@href').getall()

        top_teasers_copy = top_teasers[:]  # Create a copy of top_teasers to avoid modifying original list while iterating
        for href in top_teasers_copy:
            if href in navigation_bar:
                top_teasers.remove(href)  # Remove link from top_teasers if it is also present in navigation_bar

        for href in top_teasers:
               yield response.follow(url = href, callback = self.parse_links)

    def topic_to_article(self, response):
        articles = response.xpath('//*[@id="sueddeutsche"]/div/main//div/ul//li/section/div//article//a/@href').getall()
        for href in articles:
            yield response.follow(url = href, callback = self.parse_links)

    def parse_links(self, response):
        article_title = response.xpath('//*[@id="article-app-container"]/article//div/div/header/h2//span/text()').getall()
        article_body = response.xpath('//p[@data-manual="teaserText"]/text()').getall()
        article_body += response.xpath('//p[@data-manual="paragraph"]/text()').getall()
        remove_signs = ['\xa0', '\n', '<\i>', '<i>', '\u2002  ']
        for i in range(len(article_body)):
            for sign in remove_signs:
                article_body[i] = article_body[i].replace(sign, '')
        
        published = response.xpath('//time[@datetime]/text()').getall()
        article_item = DrItem()

        # print('----------------------------------------------NEW ARTICLE----------------------------------------')
        article_item['article_title'] = article_title
        article_item['article_body'] = article_body
        article_item['suppliers_ID_unique'] = None
        article_item['published'] = published
        article_item['tag'] = None
        article_item['link'] = response.url
        article_item['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        article_item['truth'] = None

        # add tags according to link category
        # Define regular expressions and tags as key-value pairs in a dictionary
        regex_dict = {
            r'https://www.sueddeutsche.de/muenchen.*'                           : 'indland',
            r'https://www.sueddeutsche.de/thema/Bundesregierung.*'              : 'indland',
            r'https://www.sueddeutsche.de/bayern.*'                             : 'indland',
            r'https://www.sueddeutsche.de/wirtschaft.*'                         : 'penge',
            r'https://www.sueddeutsche.de/thema/Geldanlage.*'                   : 'penge',
            r'https://www.sueddeutsche.de/thema/Reden_wir_%C3%BCber_Geld*'      : 'penge',
            r'https://www.sueddeutsche.de/thema/Wirtschaftspolitik.*'           : 'penge',
            r'https://www.sueddeutsche.de/thema/Deutschland.*'                  : 'penge',
            r'https://www.sueddeutsche.de/thema/Banken_und_Finanzindustrie.*'   : 'penge',
            r'https://www.sueddeutsche.de/thema/Haus_kaufen.*'                  : 'penge',
            r'https://www.sueddeutsche.de/thema/Nachhaltig_Geld_anlegen.*'      : 'penge',
            r'https://www.sueddeutsche.de/gesundheit*'                          : 'health',
            r'https://www.sueddeutsche.de/bildung.*'                            : 'social',
            r'https://www.sueddeutsche.de/wissen/.*'                            : 'social',
            r'https://www.sueddeutsche.de/politik/.*'                           : 'politik',
            r'https://www.sueddeutsche.de/thema/Klimawandel.*'                  : 'miljø',
            r'https://www.sueddeutsche.de/thema/Klimapolitik.*'                 : 'miljø',
            r'https://www.sueddeutsche.de/thema/Klimaprotest.*'                 : 'miljø',
            r'https://www.sueddeutsche.de/thema/Energie.*'                      : 'miljø',
            r'https://www.sueddeutsche.de/thema/Energiepolitik.*'               : 'miljø',
            r'https://www.sueddeutsche.de/thema/Erneuerbare_Energien.*'         : 'miljø',
            r'https://www.sueddeutsche.de/thema/Atomkraft.*'                    : 'miljø',
            r'https://www.sueddeutsche.de/thema/Erdgas.*'                       : 'miljø',
            r'https://www.sueddeutsche.de/thema/Fl%C3%BCssiggas.*'              : 'miljø',
            r'https://www.sueddeutsche.de/thema/Erd%C3%B6l.*'                   : 'miljø',
            r'https://www.sueddeutsche.de/thema/Windkraft.*'                    : 'miljø',
            r'https://www.sueddeutsche.de/thema/Energie_sparen.*'               : 'miljø',
            r'https://www.sueddeutsche.de/thema/Braunkohle.*'                   : 'miljø'
        }

        # Loop through the dictionary and check for matches
        for regex_pattern, tag in regex_dict.items():
            if re.compile(regex_pattern).match(response.url):
                article_item['tag'] = tag

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
        
                
        yield article_item