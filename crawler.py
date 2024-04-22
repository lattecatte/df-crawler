import scrapy
from scrapy.crawler import CrawlerProcess

from utils.filter_utils import *
from utils.weapon_utils import *
from utils.crawler_utils import *
from utils.database_utils import *

# run spider
process = CrawlerProcess(settings={
    # specify any settings if needed
    "LOG_ENABLED": False  # disable logging if not needed
})
process.crawl(ForumSpider)
process.start()

# save info to database
save_to_database()