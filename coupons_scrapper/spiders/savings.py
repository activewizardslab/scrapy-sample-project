# -*- coding: utf-8 -*-

from .base_crawler import BaseCouponsCrawler
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from urllib2 import urlopen
from lxml import etree
from scrapy import log
from ..items import CouponsItem
from scrapy import Field
import re
from time import strptime


def date_serialiser(value):
    res = value
    if 'Expires' in res:
        res = re.findall('<span>.+</span>', value)[0].replace('<span>', '').\
            replace('</span>', '')
        res = strptime(res, '%b %d, %Y')
        res = '-'.join(map(str, [res.tm_year, res.tm_mon, res.tm_mday]))
    else:
        res = ''
    return res


class MyCouponItem(CouponsItem):

    """extended coupons item"""

    expiration_date = Field(serializer=date_serialiser)
    code_end = Field()


class SavingsScrapper(BaseCouponsCrawler):

    """crawler for site http://www.savings.in"""

    my_coupons_class = MyCouponItem

    name = 'savings'
    sitemap_name_space = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    allowed_domains = ["savings.com"]
    site_map_url = 'http://www.savings.com/sitemap.xml'
    start_urls = [
        # 'http://www.savings.com/m-Starbucks-coupons.html',
        # 'http://www.savings.com/m-Puritans-Pride-coupons.html',
        # 'http://www.savings.com/m-Mrs-Fields-coupons.html',
        # 'http://www.savings.com/m-Cloud-9-Living-coupons.html',
        # 'http://www.savings.com/m-Soccer.com-coupons.html',
    ]
    rules = [
        Rule(LxmlLinkExtractor(
            allow=(
                'www.savings.com/m-'
                # 'Puritans-Pride',
                # 'Mrs-Fields-coupons',
                # 'Cloud-9-Living-coupons',
                # 'Soccer',
                # 'Starbucks'
            ),
            deny=(
                # 'savings.in/stores'
            ),
            # restrict_xpaths=('/html/body/div[2]/div',)
        ),
            callback='parse_items',
            follow=False)
    ]

    def __init__(self, *args, **kwargs):
        self.urls_grabber()
        log.msg('Stores loaded.', _level=log.INFO)

        with open('.stores.txt', 'w') as f:
            f.write('\n'.join(self.start_urls))
        super(SavingsScrapper, self).__init__(*args, **kwargs)

    store_name_path = '//*[@class="logo featured single-drop-shadow"]/img/@alt'
    store_homepage_path = \
        '//*[@class="logo featured single-drop-shadow"]/@href'
    store_logo_path = '//*[@class="logo featured single-drop-shadow"]/img/@src'
    store_description_path = \
        '//*[@id="entity-description"]/div/div[2]/p/text()'

    coupon_name_path = './/*[@class="title "]/text()'
    coupon_description_path = './/*[@class="desc"]/text()'
    coupon_code_path = './/input[@class="code"]/@value'
    coupons_selector_css = \
        'div.list-deals:not(.expired-deals) > div.module-deal'

    coupon_expiration_date_path = './/div[@class="details-full"]/ul/li'
    coupon_code_end_path = './/input[@name="property-code-partial"]/@value'

    def urls_grabber(self):
        pages = self.tree_loader(self.site_map_url,
                                 '/s:sitemapindex/s:sitemap/s:loc/text()')
        pages = [p for p in pages if 'merchants' in p]
        stores = self.parse_sites(pages)
        self.start_urls = stores

    def parse_sites(self, pages):
        stores = set()
        for s in pages:
            stores.update(self.tree_loader(s, '/s:urlset/s:url/s:loc/text()'))
        return stores

    def tree_loader(self, url, xpath):
        site_map_lines = urlopen(url).readlines()
        tree = etree.fromstringlist(site_map_lines[1:])
        res = tree.xpath(xpath, namespaces=self.sitemap_name_space)
        return res
