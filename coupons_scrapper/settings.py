# -*- coding: utf-8 -*-

# Scrapy settings for coupons_scrapper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'coupons_scrapper'

SPIDER_MODULES = ['coupons_scrapper.spiders']
NEWSPIDER_MODULE = 'coupons_scrapper.spiders'

ITEM_PIPELINES = {
    '{}.pipelines.ItemsCleaner'.format(BOT_NAME): 1,
    '{}.pipelines.StoreCsvPipeline'.format(BOT_NAME): 2,
    '{}.pipelines.CouponCsvPipeline'.format(BOT_NAME): 3,
}

# Crawl responsibly by identifying yourself (and your website)
# on the user-agent
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'
