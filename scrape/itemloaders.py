from email.policy import default
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst





## Clean up data here for each spider and prepare for storage

class DrItemLoader(ItemLoader):

    default_output_processor = TakeFirst()
    # title_in = MapCompose(lambda x: x.split('')[-1])
    link_in = MapCompose(lambda x: x.split('https://www.dr.dk/') + x )
