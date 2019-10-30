# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from ..items import DdapItem

class InspectionsSpider(scrapy.Spider):
    name = 'inspections'
    start_urls = ['http://sais.health.pa.gov/commonpoc/Content/PublicWeb/DAFind.aspx/']

    def parse(self, response):

        yield FormRequest(url="http://sais.health.pa.gov/commonpoc/Content/PublicWeb/DAFacilityInfo.aspx", formdata={
            'radio': 'on',
            'dropCounties': 'ADAMS',
            # 'dropCounties': '-All',
            'btnSubmit2': 'Find'
        }, callback=self.parse_provider_list)


    def parse_provider_list(self,response):
        self.log('On facility list page')

        rows = response.css('form#frmFacInfo > table')[1].css('tr')
        rows_without_header = rows[1:]

        # DONT FORGET TO REMOVE BRACKET NOTATION
        for count, row in enumerate(rows_without_header[0:1]):
            item = DdapItem()
            facility_id = row.css('td:nth-child(2) a::attr(href)').re_first(r'facid=(.*)')
            item['facility_name'] = row.css('td:nth-child(2) b::text').extract_first()
            item['facility_id'] = facility_id

            url_survey_list = f"http://sais.health.pa.gov/commonpoc/Content/PublicWeb/DASurveyList.aspx?facid={facility_id}"

            yield response.follow(url_survey_list, callback=self.parse_survey_list,
                                  meta={'item': item.copy()})


    def parse_survey_list(self,response):

        item = response.meta.get('item')
        self.log(f"{item['facility_id']} - {item['facility_name']}: parsing survey list")

        surveys = response.css('form#frmSurveyList table a#A1')

        # DONT FORGET TO REMOVE BRACKET NOTATION
        for survey in surveys[0:1]:
            item['event_id'] = survey.css('a').re_first('eventid=(\w*)')
            item['exit_date'] = survey.css('a').re_first('exit_date=(.*)&')

            url_survey = "http://sais.health.pa.gov/commonpoc/Content/PublicWeb/DASurveyDetails.aspx?facid={" \
                         "}&exit_date={}&eventid={}".format(item['facility_id'],item['exit_date'],item['event_id'])
            url_testing = "http://sais.health.pa.gov/commonpoc/Content/PublicWeb/DASurveyDetails.aspx?facid=IHK46601&exit_date=02/14/2012&eventid=31H811"

            yield response.follow(url_testing, callback=self.parse_survey,
                                  meta={'item': item.copy()})

    def parse_survey(self, response):
        item = response.meta.get('item')
        self.log(f"{item['facility_id']} - {item['facility_name']}: parsing survey page")

        item['initial_comments'] = response.css('tr:nth-child(2) td:nth-child(1)::text').extract_first()
        rows_without_initial_comments = response.css('form#frmSurveyDetails > table > tr:nth-child(2) ~ tr')

        for count, row in enumerate(rows_without_initial_comments):
            self.log(f'Row count: {count + 1}')
            if (count + 1) % 2 == 0:
                self.log('Row count is an even number - skip to next row')
                continue

            item['regulation'] = row.css('tr > td font::text').extract_first().strip()

            observations = rows_without_initial_comments[count+1]\
                .css('tr > td:nth-child(1)::text').extract()
            plan_of_correction = rows_without_initial_comments[count+1]\
                .css('tr > td:nth-child(2)::text').extract()

            item['observations'] = " ".join(observations)
            item['plan_of_correction'] = " ".join(plan_of_correction)

            yield item

