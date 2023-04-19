# # Define your item pipelines here
# # Goes for each spider

            
from itemadapter import ItemAdapter
from  data_generator.utils.sql_utils import get_database_engine, empty_database_tables
from data_generator.database.tables import Logs
from data_generator.database.datawriter import DataWriter
from data_generator.database.data_loader import DataLoader
from scrapy.exceptions import DropItem
import re


dw = DataWriter()
dl = DataLoader()

def load_data_to_db(item):
    item_list = []
    log_scraped_item = Logs(
    article_title = item['article_title'],
    article_body = item['article_body'],
    tag = item['tag'],
    link = item['link'],
    published = item['published'],
    log_time = item['log_time'],
    suppliers_ID_unique = item['suppliers_ID_unique'],
    )

    item_list.append(log_scraped_item)
    dw.write_multiple_rows_to_database(item_list)
    print('-------------------------Item wrote to database--------------------------')
    # print('-------------------------------------------------------------------')
    # print('article_title: ', '\n', item['article_title'])
    # print('-------------------------------------------------------------------')
    # print('article_body: ', '\n', item['article_body'])
    # print('-------------------------------------------------------------------')
    # print('suppliers_ID_unique: ', '\n', item['suppliers_ID_unique'])
    # print('-------------------------------------------------------------------')
    # print('published: ','\n', item['published'])
    # print('-------------------------------------------------------------------')
    # print('link: ', '\n',item['link'])
    # print('-------------------------------------------------------------------')
    # print('log_time: ', '\n',item['log_time'])
    # print('-------------------------------------------------------------------')
    # print('tag: ', '\n',item['tag'])
    # print('-------------------------------------------------------------------')


class DublicatePipeline:
    
    def __init__(self):
        self.link_seen = set()
        # remove none important links websites
        self.remove_patterns = {
            'drudland': [
                re.compile(r'https://www.dr.dk/nyheder/engagement/.*'),
                re.compile(r'https://www.dr.dk/nyheder/stories/.*'),
                re.compile(r'https://www.dr.dk/nyheder/regionale/.*')
            ],
            'drpolitik': [
                re.compile(r'https://www.dr.dk/nyheder/engagement/.*'),
                re.compile(r'https://www.dr.dk/nyheder/stories/.*'),
                re.compile(r'https://www.dr.dk/nyheder/regionale/.*')
            ],
            'drpenge': [
                re.compile(r'https://www.dr.dk/nyheder/engagement/.*'),
                re.compile(r'https://www.dr.dk/nyheder/stories/.*'),
                re.compile(r'https://www.dr.dk/nyheder/regionale/.*')
            ],
            'drindland': [
                re.compile(r'https://www.dr.dk/nyheder/engagement/.*'),
                re.compile(r'https://www.dr.dk/nyheder/stories/.*'),
                re.compile(r'https://www.dr.dk/nyheder/regionale/.*')
            ],
            'politikken': [
                re.compile(r'https://politiken.dk/podcast/.*'),
                re.compile(r'https://politiken.dk/sport/.*'),
                re.compile(r'https://politiken.dk/forbrugerliv/.*'),
                re.compile(r'https://politiken.dk/del/.*'),
                re.compile(r'https://politiken.dk/kultur/.*'),
                re.compile(r'https://politiken.dk/News_in_Russian/.*'),
                re.compile(r'https://politiken.dk/byen/.*'),
            ],
            'finans': [
                re.compile(r'https://finans.dk/karriere/.*'),
                re.compile(r'https://finans.dk/debat/.*'),
                re.compile(r'https://finans.dk/privat/.*'),
                re.compile(r'https://finans.dk/navne/.*'),
                re.compile(r'https://finans.dk/weekend/.*'),
                re.compile(r'https://finans.dk/podcast/.*'),
            ],
            'bbc': [
                re.compile(r'https://www.bbc.com/future.*'),                        # dobbelt check alle disse i excel efterfølgende for noget med samme link
                re.compile(r'https://www.bbc.com/sport.*'),
                re.compile(r'https://www.bbc.com/news/entertainment_and_arts.*'),
                re.compile(r'https://www.bbc.com/news/stories.*'),
                re.compile(r'https://www.bbc.com/news/av/.*'),
                re.compile(r'https://www.bbc.com/news/world_radio_and_tv/.*'),
                re.compile(r'https://www.bbc.com/news/in_pictures/.*'),
                re.compile(r'https://www.bbc.com/news/reality_check/.*'),
                re.compile(r'https://www.bbc.com/news/newsbeat/.*'),
                re.compile(r'https://cloud.*'),
                re.compile(r'https://www.bbc.com/culture.*'),
                re.compile(r'https://www.bbc.com/worklife.*'),
                re.compile(r'https://www.bbc.co.uk/usingthebbc.*'),
                re.compile(r'https://www.bbc.co.uk/iplayer.*'),
                re.compile(r'https://www.bbc.co.uk/travel.*'),
                re.compile(r'https://www.bbc.com/news/topics.*'),
                re.compile(r'https://www.bbc.com/news/world/'),
                re.compile(r'https://www.bbc.com/news/world/us_and-.*'),
                re.compile(r'https://www.bbc.com/news/world-asia-.*'),
                re.compile(r'https://www.bbc.com/news/world-africa-.*'),
                re.compile(r'https://www.bbc.com/news/world-us-.*'),
                
                re.compile(r'https://twitter.com.*'),
                re.compile(r'Follow Matt on Twitter '),

                re.compile(r'https://www.bbc.co.uk/future.*'),
                re.compile(r'https://www.bbc.co.uk/sport.*'),
                re.compile(r'https://www.bbc.co.uk/news/entertainment_and_arts.*'),
                re.compile(r'https://www.bbc.co.uk/news/stories.*'),
                re.compile(r'https://www.bbc.co.uk/news/av/.*'),
                re.compile(r'https://www.bbc.co.uk/news/world_radio_and_tv/.*'),
                re.compile(r'https://www.bbc.co.uk/news/in_pictures/.*'),
                re.compile(r'https://www.bbc.co.uk/news/reality_check/.*'),
                re.compile(r'https://www.bbc.co.uk/news/newsbeat/.*'),
                re.compile(r'https://www.bbc.co.uk/culture.*'),
                re.compile(r'https://www.bbc.co.uk/worklife.*'),
                re.compile(r'https://www.bbc.co.uk/usingthebbc.*'),
                re.compile(r'https://www.bbc.co.uk/iplayer.*'),
                re.compile(r'https://www.bbc.co.uk/travel.*'),
                re.compile(r'https://www.bbc.co.uk/news/topics.*'),
                re.compile(r'https://www.bbc.co.uk/food.*')
            ],
            'thesun': [
                re.compile(r'https://www.thesundaily.my/cerita.*'),
                re.compile(r'https://www.thesundaily.my/sport/.*'),
                re.compile(r'https://www.thesundaily.my/gear-up/.*'),
            ],
            'bild': [
                re.compile(r'https://www.bild.de/news/mystery-themen/mystery/home-15682164.bild.html'),
                re.compile(r'https://www.bild.de/news/einherzfuerkinder/ein-herz-fuer-kinder/home-15682108.bild.html'),
                re.compile(r'https://www.bild.de/corporate-site/newsletter/bild-service/newsletter-44536448.bild.html'),
                re.compile(r'https://www.bild.de/schlagzeilen-des-tages/ateaserseite/der-tag-bei-bild/ateaserseite-15480098.bild.html'),
                re.compile(r'/video/mediathek/video/bild-live-71144736.bildMobile.html'),
                re.compile(r'https://m.bild.de/lifestyle/.*'),
                re.compile(r'https://angebot.bild.de/info.*'),
                re.compile(r'https://www.bild.de/suche.bild.html'),
                re.compile(r'https://m.wetter.bild.de/.*'),
                re.compile(r'https://www.bild.de/newsletter.*'),
                re.compile(r'https://epaper.bild.de/.*'),
                re.compile(r'/bild-mobil/mdot/kinostarts-der-woche/aktuelle-filme-im-kino-19629036.bildMobile.html'),
                re.compile(r'/suche.bildMobile.html'),
                re.compile(r'https://shop.bild.de/.*'),
                re.compile(r'/digital/mobil/bild-apps/bild-app-bildplus-abo-smartphone-tablet-smart-tv-43955250.bildMobile.html'),
                re.compile(r'https://www.autobild.de/.*'),
                re.compile(r'https://www.computerbild.de/.*'),
                re.compile(r'/deals/.*'),
                re.compile(r'/bildplus/.*'),
                re.compile(r'https://gutscheine.bild.de/.*'),
                re.compile(r'https://sportwetten.bild.de/.*'),
                re.compile(r'https://spiele.bild.de/.*'),
                re.compile(r'https://www.bildbet.de/de-de?affid=27318&btagid=92306949&utm_campaign=bildnavi&utm_content=integration&utm_medium=display&utm_source=bild'),
                re.compile(r'/video/clip/.*'),

                re.compile(r'https://www.bild.de/bild-plus/.*'),
            ],
            'sueddeutsche': [
                re.compile(r'https://www.sueddeutsche.de/thema/Essen_und_Trinken.*$'),
                re.compile(r'https://www.sueddeutsche.de/projekte/.*$'),
                re.compile(r'http://www.jetzt.de.*$'),
                re.compile(r'https://www.sueddeutsche.de/news?search=.*$'),
                re.compile(r'https://sz-magazin.sueddeutsche.de/.*$'),
                re.compile(r'https://www.sueddeutsche.de/medien/.*$'),
                re.compile(r'https://www.sueddeutsche.de/tools/.*$'),
                re.compile(r'https://www.sueddeutsche.de/autoren.*$'),
                re.compile(r'https://www.sueddeutsche.de/thema/Donald_Trump.*$'),
                re.compile(r'https://pressemitteilungen.sueddeutsche.de/.*$'),
                re.compile(r'https://www.sueddeutsche.de/vergleich/.*$'),
                re.compile(r'https://englisch.sueddeutsche.de/.*$'),
                re.compile(r'https://www.sueddeutsche.de/firmen.*$'),
                re.compile(r'https://szshop.sueddeutsche.de/.*$'),
                re.compile(r'https://immobilienmarkt.sueddeutsche.de.*$'),
                re.compile(r'https://www.sueddeutsche.de/thema/Quiz.*$'),
                re.compile(r'https://www.sueddeutsche.de/thema/Und_nun_zum_Sport.*$'),
                re.compile(r'https://www.sueddeutsche.de/sport/.*$'),
                re.compile(r'https://www.sueddeutsche.de/thema/Schach-WM.*$'),
                re.compile(r'https://www.sueddeutsche.de/thema/Video.*$'),
                re.compile(r'https://www.sueddeutsche.de/panorama/.*$'),
                re.compile(r'https://www.sueddeutsche.de/thema/Podcast.*$'),
                re.compile(r'https://www.sueddeutsche.de/thema/Immobilien_und_Wohnen.*$'),
                re.compile(r'https://www.sueddeutsche.de/thema/Neuhausen.*$'),
                re.compile(r'https://www.sueddeutsche.de/kolumne/.*$'),
                re.compile(r'https://www.sueddeutsche.de/vergleich/.*$'),
            ],
            'reuters': [
                re.compile(r'https://www.reuters.com/world/us.*'),
                re.compile(r'https://www.reuters.com/markets/asia.*'),
                re.compile(r'https://www.reuters.com/markets/quote.*'),
                re.compile(r'https://www.reuters.com/markets/rates-bonds.*'),
                re.compile(r'https://www.reuters.com/markets/rates-bonds.*'),
                re.compile(r'https://www.reuters.com/markets/us/.*'),
                re.compile(r'https://www.reuters.com/world/india.*'),
                re.compile(r'https://www.reuters.com/investigates/.*'),
           ]

        }
    
    def process_item(self, item, spider):
        print('-------------------------PROCESS ITEM--------------------------')      
        # remove non-important links based on spider name
        if spider.name in self.remove_patterns:
            print(f'-------------------------{spider.name.upper()}-------------------------------------------')
            print(f'-------------------------{spider.name.upper()}-------------------------------------------')
            for pattern in self.remove_patterns[spider.name]:
                if pattern.match(item['link']):
                    print('-------------------------INSIDE IF -> REMOVE LINK--------------------------')
                    raise DropItem(f"Non-important link found: {item['link']} FROM {spider.name}")
        
        # check if item link has already been seen
        if item['link'] in self.link_seen:
            print('-------------------------INSIDE IF -> REMOVE ITEM LINK SEEN--------------------------')
            raise DropItem(f"Duplicate item found: {item['link']} FROM {spider.name}")
        else:
            print('-------------------------ELSE -> ADD NEW LINK--------------------------')
            self.link_seen.add(item['link'])
            load_data_to_db(item)
    
        return item

