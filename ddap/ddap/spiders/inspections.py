# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from ..items import DdapItem



class InspectionsSpider(scrapy.Spider):
    name = 'inspections'
    start_urls = ['http://sais.health.pa.gov/commonpoc/Content/PublicWeb/DAFind.aspx']

    def parse(self, response):

        # Getting all counties with the exception of first, '-All'
        county_list = response.css('select#dropCounties option::attr(value)').extract()[1:]
        self.log(f"Facilities from the following providers will be scraped: {county_list}")

        county_list = [county.upper() for county in county_list]

        for county in county_list:

            yield FormRequest(url="http://sais.health.pa.gov/commonpoc/Content/PublicWeb/DAFacilityInfo.aspx", formdata={
                'radio': 'on',
                'dropCounties': county,
                'btnSubmit2': 'Find'
            }, callback=self.parse_provider_list, meta={'county': county})


    def parse_provider_list(self,response):
        county = response.meta.get('county')
        self.log(f'Getting facilities in {county}...')

        fac_info_tables = response.css('form#frmFacInfo > table')

        if fac_info_tables:
            self.log(f'{county } County: Facilities found')
            rows = fac_info_tables[1].css('tr')
            rows_without_header = rows[1:]

            for count, row in enumerate(rows_without_header):
                item = DdapItem()
                facility_id = row.css('td:nth-child(2) a::attr(href)').re_first(r'facid=(.*)')
                item['facility_name'] = row.css('td:nth-child(2) b::text').extract_first()
                item['facility_id'] = facility_id
                item['facility_county'] = county

                url_survey_list = f"http://sais.health.pa.gov/commonpoc/Content/PublicWeb/DASurveyList.aspx?facid={facility_id}"

                yield response.follow(url_survey_list, callback=self.parse_survey_list,
                                      meta={'item': item.copy()})
        else:
            self.log(f'{county } County: No facilities found!')



    def parse_survey_list(self,response):

        item = response.meta.get('item')
        self.log(f"{item['facility_id']} - {item['facility_name']}: parsing survey list")

        surveys = response.css('form#frmSurveyList table a#A1')

        for survey in surveys:
            item['event_id'] = survey.css('a').re_first('eventid=(\w*)')
            item['exit_date'] = survey.css('a').re_first('exit_date=(.*)&')

            url_survey = "http://sais.health.pa.gov/commonpoc/Content/PublicWeb/DASurveyDetails.aspx?facid={" \
                         "}&exit_date={}&eventid={}".format(item['facility_id'],item['exit_date'],item['event_id'])
            yield response.follow(url_survey, callback=self.parse_survey,
                                  meta={'item': item.copy()})

    def parse_survey(self, response):
        item = response.meta.get('item')
        self.log(f"{item['facility_id']} - {item['facility_name']}: parsing survey page")

        item['initial_comments'] = response.css('tr:nth-child(2) td:nth-child(1)::text').extract_first()
        rows_without_initial_comments = response.css('form#frmSurveyDetails > table > tr:nth-child(2) ~ tr')

        if rows_without_initial_comments:
            for count, row in enumerate(rows_without_initial_comments):
                self.log(f'Row count: {count + 1}')

                # We only want odd rows because they contain the regulation value
                if (count + 1) % 2 == 0:
                    self.log('Row count is an even number - skip to next row')
                    continue

                # In rare cases, another row with 'initial comments' appears within rows_without_initial_comments
                if row.css('td b::text').re_first('INITIAL COMMENTS'):
                    self.log("STRANGE - 'INITIAL COMMENTS' detected in row - skip to next row")
                    continue

                regulation = row.css('tr > td font::text').extract_first()
                item['regulation'] = self.clean_field(regulation, item['facility_id'])
                observations = rows_without_initial_comments[count+1]\
                    .css('tr > td:nth-child(1)::text').extract()
                plan_of_correction = rows_without_initial_comments[count+1]\
                    .css('tr > td:nth-child(2)::text').extract()

                item['observations'] = " ".join(observations)
                item['plan_of_correction'] = " ".join(plan_of_correction)

                yield item

        else:
            field_names = ['regulation','observations','plan_of_correction']
            for field in field_names:
                item[field] = None

            yield item


    def clean_field(self, value, facility_id):
        if value:
            return value.strip()
        else:
            self.log(f"STRANGE - encountered 'None' when cleaning value for {facility_id}")
            return value


