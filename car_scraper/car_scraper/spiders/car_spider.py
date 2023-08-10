import scrapy
import re
from scrapy_splash import SplashRequest


class CarSpider(scrapy.Spider):
    name = "car_spider"
    start_urls = ['https://eng.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&j%5B0%5D=1&j%5B1%5D=2&j%5B2%5D=3&j%5B3%5D=4&j%5B4%5D=5&j%5B5%5D=6&j%5B6%5D=61&j%5B7%5D=67&j%5B8%5D=7&j%5B9%5D=8&j%5B10%5D=69&j%5B11%5D=70&ae=8&af=50&ssid=109470384']  # Replace with your actual start URL

    def start_requests(self):
        yield SplashRequest(
            url="https://eng.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&j%5B0%5D=1&j%5B1%5D=2&j%5B2%5D=3&j%5B3%5D=4&j%5B4%5D=5&j%5B5%5D=6&j%5B6%5D=61&j%5B7%5D=67&j%5B8%5D=7&j%5B9%5D=8&j%5B10%5D=69&j%5B11%5D=70&ae=8&af=50&ssid=109470384",
            callback=self.parse,
            args={
                'wait': 2,
            }
        )

    def parse(self, response):
        # Extracting the title
        title = response.css('[class^=search-filter]::text').get().strip()

        # Extracting items
        for car in response.css('#usedVehiclesSearchResult-flex .result-row'):
            link_elem = car.css('a.main')
            model = link_elem.css('span.model::text').get().strip()
            brand = link_elem.xpath('./span[position()=1]/text()').get().strip()
            engine = link_elem.css('span.engine::text').get().strip()

            price_elem = car.css('div.description div.finance span.pv span.price::text').get()
            price = int(''.join(filter(str.isdigit, price_elem)))

            year = car.css('div.description div.title span.year::text').get().strip()

            listing_url = car.css('a.row-link::attr(href)').get()

            # Image extraction
            image_style = car.css('.thumbnail .thumb::attr(style)').get()
            image_url = re.search(r"url\('(.+?)'\)", image_style).group(1) if image_style else None

            # Fuel extraction
            fuel_type = car.css('.extra .fuel::text').get()

            # Transmission extraction
            transmission_type = car.css('.extra .transmission::text').get()

            yield {
                'title': title,
                'brand': brand,
                'model': model,
                'engine': engine,
                'price': price,
                'year': year,
                'image': image_url,
                'fuel': fuel_type,
                'transmission': transmission_type,
                'link': listing_url
            }


        # If there's pagination, you can add it here. The provided code doesn't handle pagination.
