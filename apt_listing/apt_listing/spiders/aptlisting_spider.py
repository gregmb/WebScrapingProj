from scrapy import Spider, Request
from apt_listing.items import AptListingItem
from scrapy.crawler import CrawlerProcess
#import scrapoxy
from scrapy.utils.project import get_project_settings

class AptListingSpider(Spider):
	name = "aptlisting_spider"
	allowed_urls = ['https://www.trulia.com']
	start_urls = ['https://www.trulia.com/for_rent/Brooklyn,NY/' + str(i) + '_p/' for i in range(1,266)]

	def parse(self, response):
		links = response.xpath('//ul[@class="mvn row"]/li//a[1]/@href').extract()
		links = ['https://www.trulia.com'+link for link in links]

		for url in links:
			yield Request(url, callback = self.parse_apt)

	def parse_apt(self, response):
		price = response.xpath('//div[@class="h2 typeReversed typeDeemphasize man pan txtC"]/span/text()').extract_first().strip()
		street = response.xpath('//div[@id="propertyDetails"]//span[@class="headlineDoubleSub typeWeightNormal typeLowlight man"]/span[1]/text()').extract_first()
		city = response.xpath('//div[@id="propertyDetails"]//span[@class="headlineDoubleSub typeWeightNormal typeLowlight man"]/span[2]/text()').extract_first()
		state = response.xpath('//div[@id="propertyDetails"]//span[@class="headlineDoubleSub typeWeightNormal typeLowlight man"]/span[3]/text()').extract_first()
		zipcode = response.xpath('//div[@id="propertyDetails"]//span[@class="headlineDoubleSub typeWeightNormal typeLowlight man"]/span[4]/text()').extract_first()
		address = ', '.join([street, city, state, zipcode])
		neighborhood = response.xpath('//div[@id="propertyDetails"]//a[@id="neighborhood_link"]/text()').extract_first()
		bedrooms = response.xpath('//ul[@class="listBulleted listingDetails mrn mtm"]/li[1]/text()').extract_first()
		bath = response.xpath('//ul[@class="listBulleted listingDetails mrn mtm"]/li[2]/text()').extract_first()
		age = response.xpath('//ul[@class="listBulleted listingDetails mrn mtm"]/li[3]/text()').extract_first()
		description = ''.join(response.xpath('//span[@itemprop="description"]/text()').extract()).strip()
		patterns = ['//div[@id="listingHomeDetailsContainer"]/div[@class="mvl"]//text()', '//ul[@class="listInline pdpFeatureList"]/li/ul/li/text()']
		for pattern in patterns:
			features =  '; '.join(list(map(str.strip, response.xpath(pattern).extract()))).strip()
			if features:
				break
		crime = response.xpath('//div[@data-action="showCrimePopup"]/div/div/text()').extract_first().strip()
		#floorplan = list(map(str.strip, response.xpath('//tr[@class=" typeEmphasize toggleAllUnits "]/td/text()').extract()))
	
		item = AptListingItem()
		item['price'] = price
		item['address'] = address
		item['neighborhood'] = neighborhood
		item['bedrooms'] = bedrooms
		item['bath'] = bath
		item['age'] = age
		item['description'] = description
		item['features'] = features
		item['crime'] = crime
		item['site'] = ['trulia']
		#item['floorplan'] = floorplan
		yield item


