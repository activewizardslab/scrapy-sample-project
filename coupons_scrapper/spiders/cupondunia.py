# -*- coding: utf-8 -*-

from .base_crawler import BaseCouponsCrawler
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor


class CouponduniaScrapper(BaseCouponsCrawler):

    """crawler for site http://www.coupondunia.in"""

    name = 'coupondunia'
    allowed_domains = ["coupondunia.in"]
    start_urls = [
        'http://www.coupondunia.in/stores'
    ]
    rules = [
        Rule(LxmlLinkExtractor(
            allow=(
                # '1-800-mobiles-coupons',
                # 'http://promotionalcodes.com/macys-coupons',
                # 'zoffio',
                # 'ebay',
            ),
            deny=(
                'coupondunia.in/stores'
            ),
            restrict_xpaths=('/html/body/div[2]/div',)
        ),
            callback='parse_items',
            follow=False)
    ]

    def __init__(self, *args, **kwargs):
        super(CouponduniaScrapper, self).__init__(*args, **kwargs)

    store_name_path = '/html/body/div[2]/div/div/div[2]/div[1]/h1/span[1]/text()'
    store_homepage_path = '/html/body/div[2]/div/div/div[1]/div/div[1]/div/div/div/a/@href'
    store_logo_path = '/html/body/div[2]/div/div/div[1]/div/div[1]/div/div/img/@src'
    # store_description_path = '//*[@id="bodywrap"]/div/div[3]/div[1]/p/text()'

    coupon_name_path = './div/div[@class="offer-title"]/a/text()'
    coupon_description_path = './div/div[@class="offer-description-full"]/text()'
    coupon_code_path = './div/div[@class="offer-getcode"]/div/@data-code'
    coupons_selector_css = 'html body div.page-content.dark div.container div.row div.col-19 div#coupon_container.row.margin-left-right-none div.offer-big.offer.sms-parent.col-24'
