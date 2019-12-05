# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class JavbusListSpider(scrapy.Spider):
    name = 'javbus_list'
    allowed_domains = ['buscdn.work']
    # start_urls = ['http://buscdn.work/']

    def start_requests(self):
        yield Request("https://www.buscdn.work/page/2", callback=self.parse, dont_filter=True)

    def parse(self, response):
        items = response.xpath("//div[@id='waterfall']//div[@id='waterfall']/div[@class='item']")
        for item in items:
            movie_box = item.xpath("a[@class='movie-box']")
            url = movie_box.xpath("@href").extract_first()
            photo_frame = movie_box.xpath("div[@class='photo-frame']")
            img_url = photo_frame.xpath("img/@src").extract_first()
            img_title = photo_frame.xpath("img/@title").extract_first()

            photo_info = movie_box.xpath("div[@class='photo-info']/span")

            title = photo_info.xpath("text()").extract_first()

            item_tag = photo_info.xpath("div[@class='item-tag']")
            is_hd_link_flag = item_tag.xpath("button[@class='btn btn-xs btn-primary']/@disabled").extract_first()
            is_hd_link_title = item_tag.xpath("button[@class='btn btn-xs btn-primary']/@title").extract_first()
            is_hd_link_text = item_tag.xpath("button[@class='btn btn-xs btn-primary']/text()").extract_first()

            is_magnet_link_flag = item_tag.xpath("button[@class='btn btn-xs btn-success ']/@disabled").extract_first()
            is_magnet_link_title = item_tag.xpath("button[@class='btn btn-xs btn-success ']/@title").extract_first()
            is_magnet_link_text = item_tag.xpath("button[@class='btn btn-xs btn-success ']/text()").extract_first()

            bango = photo_info.xpath("date/text()")[0].extract()
            date = photo_info.xpath("date/text()")[1].extract()

            print(url)
            print(img_url)
            print(img_title)
            print(title)
            print(is_hd_link_flag)
            print(is_hd_link_title)
            print(is_hd_link_text)

            print(is_magnet_link_flag)
            print(is_magnet_link_title)
            print(is_magnet_link_text)

            print(bango)
            print(date)
        pass
