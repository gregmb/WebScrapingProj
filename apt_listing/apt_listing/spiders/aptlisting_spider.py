from scrapy import Spider, Request
from apt_listing.items import AptListingItem
from scrapy.crawler import CrawlerProcess

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
		floorplan = list(map(str.strip, response.xpath('//tr[@class=" typeEmphasize toggleAllUnits "]/td/text()').extract()))
	
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
		item['floorplan'] = floorplan
		yield item

class AptComSpider(Spider):
	name = "aptcom_spider"
	allowed_urls = ['https://www.apartments.com']
	start_urls = ['https://www.apartments.com/brooklyn-ny/' + str(i) for i in range(1, 29)]

	def parse(self, response):
		links = response.xpath('//div[@id="placardContainer"]//a/@href').extract()
		age = response.xpath('//span[@class="lastUpdated"]/span/text()').extract_first()


		for url in links:
			yield Request(url, callback = self.parse_apt, meta={'age':age})

	def parse_apt(self, response):
		price = list(map(str.strip, response.xpath('//td[@class="rent"]/text()').extract()))
		street = response.xpath('//div[@class="propertyAddress"]//span[@itemprop="streetAddress"]/text()').extract_first()
		city = response.xpath('//div[@class="propertyAddress"]//span[@itemprop="addressLocality"]/text()').extract_first() 
		state = response.xpath('//div[@class="propertyAddress"]//span[@itemprop="addressRegion"]/text()').extract_first()
		zipcode =response.xpath('//div[@class="propertyAddress"]//span[@itemprop="postalCode"]/text()').extract_first()
		address = ', '.join([street, city, state, zipcode])
		neighborhood = response.xpath('//div[@class="neighborhoodAddress"]//a/text()').extract_first()
		bedrooms = list(map(str.strip, response.xpath('//td[@class="beds"]/span[@class="shortText"]/text()').extract()))
		bath = list(map(str.strip, response.xpath('//td[@class="baths"]/span[@class="shortText"]/text()').extract()))
		age = response.meta['age']
		description = response.xpath('//p[@itemprop="description"]/text()').extract_first().strip()
		features = response.xpath('//div[@class="js-viewAnalyticsSection"]//li/text()').extract()
		SqFt = list(map(str.strip, response.xpath('//td[@class="sqft"]/text()').extract()))
		floorplan = list(map(str.strip, response.xpath('//div[@class="tabContent active"]//td//text()').extract()))

		item = AptListingItem()
		item['price'] = price
		item['address'] = address
		item['neighborhood'] = neighborhood
		item['bedrooms'] = bedrooms
		item['bath'] = bath
		item['age'] = age
		item['description'] = description
		item['features'] = features
		item['SqFt'] = SqFt
		item['site'] = ['apt.com']
		item['floorplan'] = floorplan

		yield item.strip()



class CraigslistSpider(Spider):
	name = "craigslist_spider"
	allowed_urls = ['https://newyork.craigslist.org']
	start_urls = ['https://newyork.craigslist.org/search/brk/aap?s=' + str(i) for i in range(0,3000,120)]

	def parse(self, response):
		links = response.xpath('//ul[@class="rows"]//a/@href').extract()
		links = links[0:len(links):3]

		for url in links:
			yield Request(url, callback = self.parse_apt)

	def parse_apt(self, response):
		price = response.xpath('//span[@class="price"]/text()').extract_first()
		neighborhood = response.xpath('//span[@class="postingtitletext"]/small/text()').extract_first().strip()
		bedrooms = response.xpath('//span[@class="shared-line-bubble"]/b[1]/text()').extract_first()
		bath = response.xpath('//span[@class="shared-line-bubble"]/b[2]/text()').extract_first()
		SqFt = response.xpath('//span[@class="shared-line-bubble"][2]/b/text()').extract_first()
		features = response.xpath('//p[@class="attrgroup"][2]/span/text()').extract()
		description =  ''.join(list(map(str.strip, response.xpath('//section[@id="postingbody"]/text()').extract()))).strip()
		age = response.xpath('//time[@class="date timeago"]/text()').extract_first().strip()

		item = AptListingItem()
		item['price'] = price
		item['neighborhood'] = neighborhood
		item['bedrooms'] = bedrooms
		item['bath'] = bath
		item['age'] = age
		item['description'] = description
		item['features'] = features
		item['SqFt'] = SqFt
		item['site'] = ['CraigsList']

		yield item

process = CrawlerProcess()
process.crawl(AptListingSpider)
process.crawl(AptComSpider)
process.crawl(CraigslistSpider)
process.start()

