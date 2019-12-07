# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
from io import BytesIO

import pymongo
from PIL import Image
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum

from javbus import settings


class JavbusImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        big_image = item['big_image']

        path = None
        if item and item['date'] and item['index']:
            # 这个参数的request就是上面的yield Request.通过meta传递自定义参数
            path = item['date'] + "/" + item['index'] + "/" + big_image.split('/')[-1]
        else:
            path = big_image.split('/')[-1]

        if path and os.path.exists(settings.IMAGES_STORE + "/" + path):
            # print(item['url'] + ": " + settings.IMAGES_STORE + "/" + path + " exists")
            pass
        else:
            # print(item['url'] + ": " + settings.IMAGES_STORE + "/" + path + " not exists")
            # 挂本地代理
            yield Request(big_image, meta={'item': item, 'proxy': 'http://127.0.0.1:1087'}, dont_filter=True)

        imgs = item['detail']['imgs']
        for img in imgs:
            path = None
            if item and item['date'] and item['index']:
                # 这个参数的request就是上面的yield Request.通过meta传递自定义参数
                path = item['date'] + "/" + item['index'] + "/" + img.split('/')[-1]
            else:
                path = img.split('/')[-1]

            if path and os.path.exists(settings.IMAGES_STORE + "/" + path):
                #print(item['url'] + ": " + settings.IMAGES_STORE + "/" + path + " exists")
                pass
            else:
                #print(item['url'] + ": " + settings.IMAGES_STORE + "/" + path + " not exists")
                yield Request(img, meta={'item': item, 'proxy': 'http://127.0.0.1:1087'}, dont_filter=True)

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        if item and item['date'] and item['index']:
            # 这个参数的request就是上面的yield Request.通过meta传递自定义参数
            return item['date'] + "/" + item['index'] + "/" + request.url.split('/')[-1]
        else:
            return request.url.split('/')[-1]

    def get_images(self, response, request, info):
        path = self.file_path(request, response, info)
        image = Image.open(BytesIO(response.body))
        buf = BytesIO()
        ext = response.url.split('.')[-1]
        if ext == 'jpeg' or ext == 'JPEG' or ext == 'JPG' or ext == 'jpg':
            image.save(buf, 'JPEG')
        elif ext == 'gif' or ext == 'GIF':
            image.save(buf, 'GIF')
        elif ext == 'png' or ext == 'PNG':
            image.save(buf, 'PNG')
        else:
            image.save(buf, 'JPEG')
        yield path, image, buf

    def check_gif(self, image):
        if image.format is None or image.format == 'GIF':
            return True

    def persist_gif(self, key, data, info):
        root, ext = os.path.splitext(key)
        absolute_path = self.store._get_filesystem_path(key)
        self.store._mkdir(os.path.dirname(absolute_path), info)
        f = open(absolute_path, 'wb')
        f.write(data)

    def image_downloaded(self, response, request, info):
        checksum = None
        for path, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
            width, height = image.size
            if self.check_gif(image):
                self.persist_gif(path, response.body, info)
            else:
                self.store.persist_file(path, buf, info, meta={'width': width, 'height':height},
                                        headers={'Content-Type': 'image/jpeg'})
        return checksum

    def item_completed(self, results, item, info):
        print(item['url'] + str(results))
        return item

class JavbusMongoPipeline(object):

    def open_spider(self, spider):
        self.mongo_client = pymongo.MongoClient(host='192.168.0.109', port=27017)
        self.collection = self.mongo_client.javbus.article

    def close_spider(self, spider):
        self.mongo_client.close()

    def process_item(self, item, spider):
        m = self.collection.update({'url': item['url']}, dict(item), upsert=True)
        print(m)
        return item
