# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy_splash import SplashRequest


class JavbusListSpider(scrapy.Spider):
    name = 'javbus_list'
    allowed_domains = ['buscdn.work']

    # start_urls = ['http://buscdn.work/']

    def start_requests(self):
        yield Request("https://www.buscdn.work/page/7", callback=self.parse, dont_filter=True)

    def parse(self, response):
        items = response.xpath("//div[@id='waterfall']//div[@id='waterfall']/div[@class='item']")
        for item in items:
            movie_box = item.xpath("a[@class='movie-box']")
            url = movie_box.xpath("@href").extract_first()
            photo_frame = movie_box.xpath("div[@class='photo-frame']")
            img_url = photo_frame.xpath("img/@src").extract_first()
            #img_title = photo_frame.xpath("img/@title").extract_first()

            photo_info = movie_box.xpath("div[@class='photo-info']/span")

            title = photo_info.xpath("text()").extract_first()

            item_tag = photo_info.xpath("div[@class='item-tag']")

            is_hd_link_text = item_tag.xpath("button[@class='btn btn-xs btn-primary']/text()").extract_first()

            is_magnet_link_text = item_tag.xpath("button[@class='btn btn-xs btn-success ']/text()").extract_first()

            bango = photo_info.xpath("date/text()")[0].extract()
            date = photo_info.xpath("date/text()")[1].extract()

            yield SplashRequest(url, self.parse_detail, args={
                'wait': 0.5,
            }, dont_filter=True, meta={
                "item": {
                    "url": url,
                    "img_url": img_url,
                    # "img_title": img_title,
                    "title": title,
                    "is_hd_link_text": is_hd_link_text is not None,
                    "is_magnet_link_text": is_magnet_link_text is not None,
                    "bango": bango,
                    "date": date
                }
            }
                                )
            # yield Request("https://www.buscdn.work/page/2", callback=self.parse_detail,
            #               meta={
            #                   "item": {
            #                       "url": url,
            #                       "img_url": img_url,
            #                       "img_title": img_title,
            #                       "title": title,
            #                       "is_hd_link_flag": is_hd_link_flag,
            #                       "is_hd_link_title": is_hd_link_title,
            #                       "is_hd_link_text": is_hd_link_text,
            #
            #                       "is_magnet_link_flag": is_magnet_link_flag,
            #                       "is_magnet_link_title": is_magnet_link_title,
            #                       "is_magnet_link_text": is_magnet_link_text,
            #
            #                       "bango": bango,
            #                       "date": date
            #                   }
            #               }, dont_filter=True)
        pass

    def parse_detail(self, response):
        rows = response.xpath("//table[@id='magnet-table']/tr")
        magnets = []
        for r in rows:
            items = r.xpath("td/a[contains(@href, 'magnet')]/text()")
            magnet = r.xpath("td/a[contains(@href, 'magnet')]/@href")[0]
            # sprint(items[0].extract() + " " + items[1].extract() + " " + items[2].extract() + " " + magnet.extract())
            magnets.append({
                'name': items[0].extract().strip(),
                'size': items[1].extract().strip(),
                'date': items[2].extract().strip(),
                'link': magnet.extract().strip(),
            })
        # print(response.xpath("//table[@id='magnet-table']//td//@href").extract_first())

        title = response.xpath("//div[@class='container']/h3/text()").extract_first()
        big_image = response.xpath("//div[@class='col-md-9 screencap']/a[@class='bigImage']//img/@src").extract_first()
        no_bango_title = response.xpath(
            "//div[@class='col-md-9 screencap']/a[@class='bigImage']//img/@title").extract_first()
        bango = response.xpath(
            "//div[@class='col-md-3 info']//span[contains(text(), '識別碼')]/following-sibling::*/text()").extract_first()
        date = response.xpath(
            "//div[@class='col-md-3 info']//span[contains(text(), '發行日期')]/parent::*/text()").extract_first()
        length = response.xpath(
            "//div[@class='col-md-3 info']//span[contains(text(), '長度')]/parent::*/text()").extract_first()
        company = response.xpath(
            "//div[@class='col-md-3 info']//span[contains(text(), '製作商')]/parent::*/a/text()").extract_first()
        distributor = response.xpath(
            "//div[@class='col-md-3 info']//span[contains(text(), '發行商')]/parent::*/a/text()").extract_first()
        director = response.xpath(
            "//div[@class='col-md-3 info']//span[contains(text(), '導演')]/parent::*/a/text()").extract_first()

        genres = response.xpath("//div[@class='col-md-3 info']//p[contains(text(), '類別')]"
                                "/following-sibling::*/span[@class='genre' and not(@onmouseover)]//text()").extract()

        performer = response.xpath("//div[@class='col-md-3 info']//div[@class='star-name']//text()").extract_first()

        pics = []

        # 大图
        response.xpath("//div[@id='sample-waterfall']/*[@class='sample-box']/@href")

        # 缩略图
        response.xpath("//div[@id='sample-waterfall']/*[@class='sample-box']//img/@src")

        sample_box = response.xpath("//div[@id='sample-waterfall']/*[@class='sample-box']")
        for sb in sample_box:
            pics.append({
                'thumbnail': sb.xpath("div/img/@src").extract_first(),
                'big': sb.xpath("@href").extract_first()
            })

        # 相关内容
        related = []

        a = response.xpath("//div[@id='related-waterfall']//a")
        for aa in a:
            related.append({
                "title": aa.xpath("@title").extract_first(),
                "url": aa.xpath("@href").extract_first(),
                "img": aa.xpath("div/img/@src").extract_first()
            })

        item = response.meta['item']
        item['detail'] = {
            'title': title,
            'big_image': big_image,
            'no_bango_title': no_bango_title,
            'bango': bango,
            'date': date,
            'length': length,
            'company': company,
            'distributor': distributor,
            'director': director,
            'genres': genres,
            'performer': performer,
            'magnets': magnets, #磁力链
            'pics': pics,   #图片
            'related': related
        }
        yield item
