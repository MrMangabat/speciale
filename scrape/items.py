# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DrItem(scrapy.Item):
   
    
    # define the fields for your item here like:
    id: int = scrapy.Field(default = None, primary_key = True)          # ændre navn
    article_title: str = scrapy.Field(default = None)
    article_body: str = scrapy.Field(default = None)
    tag: str = scrapy.Field(default = None)
    link: str = scrapy.Field(default = None)
    log_time:int = scrapy.Field(default = None)
    truth: str = scrapy.Field(default = None)
    published: str = scrapy.Field(default = None)
    suppliers_ID_unique: str = scrapy.Field(default = None)
    log_time: str = scrapy.Field(default = None)               # ændre navn
