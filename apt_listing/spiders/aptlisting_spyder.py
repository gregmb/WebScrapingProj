from scrapy import Spider, Request
from scrapy.selector import Selector
from apt_listing.items import AptListingItem

class AptListingSpider(Spider):
	name = "aptlisting_spyder"
	allowed_urls = ['https://www.trulia.com']
	start_urls = ['https://www.trulia.com/for_rent/Brooklyn,NY/' + str(i) + '_p/' for i in range(1,266)]

	def parse(self, response):
		links = response.xpath('//ul[@class="mvn row"]/li//a[1]/@href').extract()
		links = ['https://www.trulia.com'+link for link in links]

		for url in links:
			yield Request(url, callback = self.parse_apt)

	def parse_apt(self, response):
		street = response.xpath('//div[@id="propertyDetails"]//span[@itemprop="streetAddress"]/text()').extract_first()
		city = response.xpath('//div[@id="propertyDetails"]//span[@itemprop="addressLocality"]/text()').extract_first()
		state = response.xpath('//div[@id="propertyDetails"]//span[@itemprop="addressRegion"]/text()').extract_first()
		zipcode = response.xpath('//div[@id="propertyDetails"]//span[@itemprop="postalCode"]/text()').extract_first()
		address = street + city + state + zipcode
		neighborhood = response.xpath('//div[@id="propertyDetails"]//a[@id="neighborhood_link"]/text()').extract_first()
		bedrooms = response.xpath('//ul[@class="listBulleted listingDetails mrn mtm"]/li[1]/text()').extract_first()
		bath = response.xpath('//ul[@class="listBulleted listingDetails mrn mtm"]/li[2]/text()').extract_first()
		age = response.xpath('//ul[@class="listBulleted listingDetails mrn mtm"]/li[3]/text()').extract_first()
		description = ''.join(response.xpath('//span[@itemprop="description"]/text()').extract()).strip()
		patterns = ['list(map(str.strip, response.xpath('//div[@id="listingHomeDetailsContainer"]/div[@class="mvl"]//text()').extract()))', '','.join(response.xpath('//ul[@class="listInline pdpFeatureList"]/li/ul/li/text()').extract()).strip()' ]
		for pattern in patterns:
			features =  ','.join(response.xpath('//ul[@class="listInline pdpFeatureList"]/li/ul/li/text()').extract()).strip()
			if features:
				break
		crime = response.xpath('//div[@data-action="showCrimePopup"]/div/div/text()').extract_first().strip()

		item = AptListingItem()
		item['address'] = address
		item['neighborhood'] = neighborhood
		item['bedrooms'] = bedrooms
		item['bath'] = bath
		item['age'] = age
		item['descrition'] = description
		item['features'] = features
		item['crime'] = crime

		yield item
