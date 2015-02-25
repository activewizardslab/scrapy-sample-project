# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from itertools import count

from scrapy import Item, Field
from scrapy import log

__DEBUG__ = True


def serialize_description(value):
    """some fields serializer for dumping"""
    if value:
        return value.strip().encode('utf-8').replace('\r', '', 1000).\
            replace('\n', '', 1000).replace('\t', '', 1000).\
            replace('  ', '', 1000).strip()


def _set_first_value(inst, prop):
    if prop in inst.keys():
        if not hasattr(inst[prop], '__iter__'):
            pass
        elif len(inst[prop]) == 1:
            inst[prop] = inst[prop][0]
        elif len(inst[prop]) == 0:
            inst[prop] = None
            log.msg('No value for {}["{}"] scraped'.format(
                inst.__class__.__name__,
                prop), _level=log.WARNING)
        else:
            res_msg = 'Too many values scrapped for {}["{}"] == {}'.format(
                inst.__class__.__name__, prop, inst[prop])
            if __DEBUG__:
                log.msg(res_msg, _level=log.WARNING)
                inst[prop] = inst[prop][0]
            else:
                raise ValueError(res_msg)
    else:
        inst[prop] = ''


class CouponsItem(Item):
    _id = count(start=1, step=1)
    id = Field()
    store_id = Field()
    name = Field(default='', serializer=serialize_description)
    description = Field(serializer=serialize_description, default='')
    code = Field(default='')
    source = Field(default='')

    def __init__(self, *args, **kwargs):
        super(CouponsItem, self).__init__(*args, **kwargs)
        self['id'] = self._id.next()

    def set_first_value(self, prop):
        _set_first_value(self, prop)


class StoresItem(Item):
    _id = count(start=1, step=1)
    id = Field()
    name = Field(default='', serializer=serialize_description)
    homepage = Field(default='')
    logo = Field(default='')
    description = Field(serializer=serialize_description, default='')
    source = Field(default='')

    def __init__(self, *args, **kwargs):
        super(StoresItem, self).__init__(*args, **kwargs)
        self['id'] = self._id.next()

    def set_first_value(self, prop):
        _set_first_value(self, prop)
