# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from abc import ABCMeta

from ..items import CouponsItem, StoresItem
from urlparse import urljoin


class BaseCouponsCrawler(CrawlSpider):
    __metaclass__ = ABCMeta

    my_coupons_class = CouponsItem

    hdr = {'User-Agent': '''Mozilla/5.0 (X11; Linux x86_64)
    AppleWebKit/537.36 (KHTML, like Gecko)
    Chrome/38.0.2125.101
    Safari/537.36''',
           'Accept': '*/*',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'gzip,deflate,sdch',
           'Accept-Language': 'en-US;q=0.8,en;q=0.4',
           'Connection': 'keep-alive',
           'DNT': '1',
           }

    name = None
    allowed_domains = [
        None
    ]
    start_urls = [
        None
    ]

    rules = (
        Rule(
            LinkExtractor(
                allow=(),
                deny=(),
            ),
            callback='parse_items', follow=False
        ),
    )

    store_name_path = None
    store_homepage_path = None
    store_logo_path = None
    store_description_path = None

    coupon_name_path = None
    coupon_description_path = None
    coupon_code_path = None

    coupons_selector_css = None

    def parse_items(self, response):
        res = []
        res.append(self.parse_store(response))
        res.extend(self.parse_coupon(response, res[0]))
        return res

    def parse_store(self, response):
        store_loader = ItemLoader(item=StoresItem(), response=response)

        store_loader.add_xpath('name', self.store_name_path)
        store_loader.add_xpath('homepage', self.store_homepage_path)
        store_loader.add_xpath('logo', self.store_logo_path)
        store_loader.add_xpath('description', self.store_description_path)
        store_loader.add_value('source', response.url)

        store_item = store_loader.load_item()
        # if hasattr(store_item, 'homepage'):
        try:
            if store_item['homepage'][0].startswith('/'):
                store_item['homepage'] = \
                    urljoin(response.url, store_item['homepage'][0].strip())
        except Exception as e:
            print(store_item)
            raise e

        return store_item

    def parse_coupon(self, response, store_item):
        res = []
        items_response = response.css(self.coupons_selector_css)

        for raw_item in items_response:
            item = self.my_coupons_class()
            item['name'] = raw_item.xpath(self.coupon_name_path).extract()
            item['description'] = raw_item.xpath(
                self.coupon_description_path).extract()
            item['code'] = raw_item.xpath(self.coupon_code_path).extract()
            item['store_id'] = store_item.get('id')
            item['source'] = store_item.get('source')
            # process extra fields
            for f in self.extra_fields:
                extra_path = getattr(self, 'coupon_{}_path'.format(f), '')
                try:
                    item[f] = raw_item.xpath(extra_path).extract()
                except Exception as e:
                    print(extra_path, f)
                    raise e

            res.append(item)

        return res

    def __init__(self, *args, **kwargs):
        self.extra_fields = set(self.my_coupons_class.fields.keys()) -\
            set(CouponsItem.fields.keys())
        super(BaseCouponsCrawler, self).__init__(*args, **kwargs)
