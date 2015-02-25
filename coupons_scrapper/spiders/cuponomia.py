# -*- coding: utf-8 -*-

from .base_crawler import BaseCouponsCrawler
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor


class CuponomiaScrapper(BaseCouponsCrawler):

    """crawler for site http://www.coupondunia.in"""

    name = 'test'
    allowed_domains = ["promotionalcodes.com"]
    start_urls = [
        'http://www.promotionalcodes.com/stores-by-letter/m'
    ]
    rules = [
        Rule(LxmlLinkExtractor(
            allow=(
                # '1-800-mobiles-coupons',
                'http://promotionalcodes.com/macys-coupons'
            )
        ),
            callback='parse_items',
            follow=False)
    ]

    def __init__(self, *args, **kwargs):
        super(CuponomiaScrapper, self).__init__(*args, **kwargs)

    store_name_path = '//*[@id="bodywrap"]/div/div[3]/div[1]/h2/a/text()'
    store_homepage_path = '//*[@id="bodywrap"]/div/div[3]/div[1]/h2/a/@href'
    store_logo_path = '//*[@id="bodywrap"]/div/div[1]/div/div/img/@src'
    store_description_path = '//*[@id="bodywrap"]/div/div[3]/div[1]/p/text()'

    coupon_name_path = './h3/a/text()'
    coupon_description_path = './p/text()'
    coupon_code_path = '/html/body/div[3]/div[1]/div[5]/div[2]/div[1]/div/article[1]/div[1]/div[1]/div[2]/div[2]/p/a/span[2]/text()'
    coupons_selector_css = 'div.coupon_box.widecoupon:not(.widecoupon-expired):not(.widecoupon-addCouponForm) > div.coupon_content > div.coupon_main_column'
