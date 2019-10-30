# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DdapItem(scrapy.Item):
    # define the fields for your item here like:
    facility_name = scrapy.Field()
    facility_id = scrapy.Field()
    facility_county = scrapy.Field()
    event_id = scrapy.Field()
    exit_date = scrapy.Field()
    initial_comments = scrapy.Field()
    regulation = scrapy.Field()
    observations = scrapy.Field()
    plan_of_correction = scrapy.Field()
