import scrapy
import re
from scrapy_splash import SplashRequest


class CarSpider(scrapy.Spider):
    name = "car_spider"
    start_urls = ['https://eng.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&j%5B0%5D=1&j%5B1%5D=2&j%5B2%5D=3&j%5B3%5D=4&j%5B4%5D=5&j%5B5%5D=6&j%5B6%5D=61&j%5B7%5D=67&j%5B8%5D=7&j%5B9%5D=8&j%5B10%5D=69&j%5B11%5D=70&ae=8&af=50&ssid=109470384']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
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

            year = car.css('div.description div.title span.year::text').get().strip()

            # Image extraction
            image_style = car.css('.thumbnail .thumb::attr(style)').get()
            image_url = re.search(r"url\('(.+?)'\)", image_style).group(1) if image_style else None

            # Fuel extraction
            fuel_type = car.css('.extra .fuel::text').get()

            # Transmission extraction
            transmission_type = car.css('.extra .transmission::text').get()

            listing_url = response.urljoin(car.css('a.row-link::attr(href)').get())

            # Create a dictionary for basic car details
            car_details = {
                'title': title,
                'brand': brand,
                'model': model,
                'engine': engine,
                'year': year,
                'image': image_url,
                'fuel': fuel_type,
                'transmission': transmission_type,
                'link': listing_url
            }

            # Send a request to the detailed ad page and pass the basic car details
            yield scrapy.Request(listing_url, callback=self.parse_ad_details, meta={'car_details': car_details})

    def parse_ad_details(self, response):
        # Get the basic car details passed from the previous method
        details = response.meta['car_details']

        # Define the preset sections
        preset_sections = {
            'Safety and security equipment': [],
            'Comfort equipment': [],
            'Interior': [],
            'Audio, video, communication': [],
            'Tires and wheels': [],
            'Lights': [],
            'Sport equipment': [],
            'Other equipment': []
        }

        for row in response.css('table.main-data tr'):
            label = row.css('td.label span::text').get()
            value = row.css('td.field span.value::text').get()

            if label == "Bodytype":
                details['body_type'] = value
            elif label == "Initial reg":
                details['initial_registration_date'] = value
            elif label == "Drive":
                details['wheel_drive'] = value
            elif label == "Color":
                details['color'] = value
            elif label == "VIN":
                details['vin'] = value
            elif label == "Price" and value:
                # Remove 'EUR' and convert to integer
                details['price'] = int(re.sub(r'\D', '', value))
            elif label == "Bargain price" and value:
                # Remove 'EUR' and convert to integer
                details['discount_price'] = int(re.sub(r'\D', '', value))
            elif label == "Mileage" and value:
                # Remove 'km' and convert to integer
                details['mileage'] = int(value.replace('km', '').replace(' ', ''))

        # Extracting from 'Car Details' HTML Element
        sections_elements = response.css('.vEquipment .vFlexColumns .equipment')

        for section_element in sections_elements:
            # Extract all h3 headings and ul groups within this section element
            headings = section_element.css('h3.heading::text').getall()
            item_groups = section_element.css('ul.group')

            # Ensure we have the same number of headings and item groups
            if len(headings) == len(item_groups):
                for i in range(len(headings)):
                    section_name = headings[i].strip()
                    if section_name in preset_sections:
                        items = item_groups[i].css('li.item::text').getall()
                        preset_sections[section_name] = items

        # Merge preset_sections into details
        details.update(preset_sections)

        # Extracting from 'Other Info' HTML Element
        status_text = response.css('.other-info .-status::text').get()
        inspection_date = response.css('.other-info .-status b::text').get()

        if inspection_date:
            status_text += ", inspection valid until " + inspection_date

        details['status'] = status_text.strip() if status_text else None
        brought_from = response.css('.other-info .-brought_from b::text').get()
        details['brought_from'] = brought_from.strip() if brought_from else None
        location = response.css('.other-info .-location b::text').get()
        details['location'] = location.strip() if location else None
        user_info = response.css('.other-info .-user_other::text').getall()
        details['user_info'] = [info.strip() for info in user_info if info.strip()]

        yield details




