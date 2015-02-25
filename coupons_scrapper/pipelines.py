# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import urllib

import shutil
import urllib2
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
from urlparse import urlparse

from items import CouponsItem, StoresItem

from abc import ABCMeta, abstractmethod
import imghdr
import os
from scrapy import log


def get_fields_cleaner(item, *fields):
    for f in fields:
        item.set_first_value(f)


class ItemsCleaner(object):

    """Clean raw values of items"""

    def process_item(self, item, spider):
        if issubclass(item.__class__, CouponsItem):
            self.clean_coupon(item, spider)
        elif issubclass(item.__class__, StoresItem):
            self.clean_store(item, spider)
        else:
            raise Exception(
                'Unknown item type! {}, [{}]'.format(item, type(item)))
        return item

    def clean_coupon(self, item, spider):
        fields_list = [
            'name',
            'description',
            'code',
            'source',
        ]
        # extra fields
        extra_fields = set(item.fields.keys()) - set(CouponsItem.fields.keys())
        for f in extra_fields:
            fields_list.append(f)
        get_fields_cleaner(item, *fields_list)
        for f in item.fields.keys():
            if f + '_end' in item.fields.keys() and item[f] and item[f + '_end']:
                item[f] = item[f] + item[f + '_end']
        return item

    def clean_store(self, item, spider):
        get_fields_cleaner(item,
                           'name',
                           'description',
                           'source',
                           'logo',
                           'homepage',
                           )

        item['homepage'] = '{0.scheme}://{0.netloc}'.format(
            urlparse(self.get_url(item['homepage'], spider)))
        if item['homepage'] == '://':
            item['homepage'] = ''
        item['logo'] = self.get_logo(item['logo'], item['id'])
        return item

    def parse_js_redirect(self, url, spider):
        res = []
        try:
            req = urllib2.Request(url, headers=spider.hdr)
            connection = urllib2.urlopen(req)
            body = connection.read()
            pattern = re.compile('(window\.location\.replace\(\')(.*)(\'\))')
            for match in pattern.finditer(body):
                res.append(match.groups()[1])
        except:
            pass
        if len(res) != 1:
            res = [url]
        return res

    def get_url(self, url, spider):
        res = ''
        request = urllib2.Request(url, headers=spider.hdr)
        try:
            res = urllib2.urlopen(request).url
        except urllib2.HTTPError as e:
            res = e.url
            log.msg(e, _level=log.ERROR)
        except urllib2.URLError as e:
            res = e.reason.strerror
            log.msg(e, _level=log.ERROR)
        except Exception as e:
            res = e.message
            log.msg(e, _level=log.ERROR)

        redirect = self.parse_js_redirect(res, spider)
        if len(redirect) == 1:
            res = redirect[0]
        return res

    def get_logo(self, url, id):
        logo_filename = ''
        if url:
            try:
                obj = urllib.urlretrieve(url.encode('utf-8'),
                                         logo_filename)
                ext = imghdr.what(obj[0])
                logo_filename = '{}_original.{}'.format(
                    id,
                    ext
                )
                shutil.move(
                    obj[0],
                    os.path.join(os.curdir, logo_filename)
                )
            except IOError as e:
                print(e)

        return logo_filename


class BaseCsvPipeline(object):
    __metaclass__ = ABCMeta

    out_file = None
    fields_to_export = []

    def __init__(self):
        """docstring for __init__"""
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file = open(self.out_file, 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file,
                                        fields_to_export=self.fields_to_export)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        if self.check_type(item):
            self.exporter.export_item(item)
        return item

    @abstractmethod
    def check_type(self, item):
        pass


class StoreCsvPipeline(BaseCsvPipeline):
    out_file = 'stores.csv'
    fields_to_export = ['id',
                        'name',
                        'homepage',
                        'logo',
                        'description',
                        'source',
                        ]

    def check_type(self, item):
        return 'store_id' not in item.keys()


class CouponCsvPipeline(BaseCsvPipeline):
    out_file = 'coupons.csv'
    fields_to_export = ['id',
                        'store_id',
                        'name',
                        'description',
                        'code',
                        'source',
                        ]

    def check_type(self, item):
        res = 'store_id' in item.keys()
        if res:
            diff = set(item.fields.keys()) - set(self.fields_to_export) -\
                set(f + '_end' for f in self.fields_to_export)
            if len(diff) > 0:
                for f in diff:
                    self.fields_to_export.append(f)
        return res
