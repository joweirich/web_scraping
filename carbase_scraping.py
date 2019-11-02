from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.settings import Settings

class CarsSpider(scrapy.Spider):
    name = 'cars'
    def __init__(self):
        self.urls = 'Search?SearchTypeID=2&Make=Chevrolet&Model=Tahoe&BodyStyle=&SubBodyStyle=&MinModelYear=&MaxModelYear=&MinPrice=3000&MaxPrice=10000&FromEstimatedMonthlyPayment=&ToEstimatedMonthlyPayment=&MaxMileage=&FromFuelEconomy=&Radius=100&ZipCode=32456&State=&City=&FullStateName=&Latitude=&Longitude=&Conditions=&HideRepairable=&FilterImageless=&PricedVehiclesOnly=&OrderBy=Relevance&OrderDirection=desc&PageResultSize=15&PageNumber=1&TotalRecords=&FromDate=&ToDate=&DaysListed=&SourceId=&SourceExternalUserID='
        
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")
        

class JobSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["craigslist.org"]
    allowed_domains = ["realtor.com"]
    allowed_domains = ["bilbasen.dk"]
    start_urls = ['https://newyork.craigslist.org/search/egr']
    start_urls = ['https://www.realtor.com/realestateandhomes-search/32456']
    start_urls = ['https://www.bilbasen.dk/brugt/bil/Mazda/6?Fuel=0&YearFrom=0&YearTo=0&PriceFrom=0&PriceTo=10000000&MileageFrom=-1&MileageTo=10000001&IncludeEngrosCVR=true&IncludeLeasing=true']

    def parse(self, response):
        xpth = '//*[@class="row listing listing-plus bb-listing-clickable"]'
        questions = response.selector.xpath(xpth)
        
        for question in questions:
            extr = question.xpath('//*[@class="col-xs-6"]//span').extract()
            print(extr)

if __name__=="__main__":
    spider = JobSpider()
    crawler = CrawlerProcess(Settings())
    crawler.crawl(spider)
    crawler.start()
