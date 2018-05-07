#!/usr/local/env python3
# -*- coding: utf-8 -*-

from scrapy.spiders import Spider, Request
import json
import os

class EhentaiSpider(Spider):
    name = 'ehentai'
    allow_domains = 'e-hentai.org'

    def start_requests(self):
            url = 'https://e-hentai.org/'

            yield Request(url=url, callback=self.ehentai_parse_front_page)
            # yield Request(url=url, callback=self.test)

    def ehentai_parse_front_page(self, response):
        last_page = response.xpath('/html/body/div[1]/div[2]/table[1]/tr/td[12]/a/text()').extract_first()

        # for i in range(0, last_page):
        for i in range(0, 1):
            purl = 'https://e-hentai.org/?page=' + str(i)
            yield Request(url=purl, callback=self.ehentai_parse_front_page_list, meta={
                'page': i + 1
            })

    def ehentai_parse_front_page_list(self, response):
        page = response.meta['page']
        for i in range(2, 28):
            if i == 14:
                continue
            # list
            category = response.xpath(
                '/html/body/div[1]/div[2]/table[2]/tr[' + str(i) + ']/td[1]/a/img/@alt').extract_first()
            publish = response.xpath(
                '/html/body/div[1]/div[2]/table[2]/tr[' + str(i) + ']/td[2]/text()').extract_first()
            name = response.xpath(
                '/html/body/div[1]/div[2]/table[2]/tr[' + str(i) + ']/td[3]/div/div[3]/a/text()').extract_first()
            alink = response.xpath(
                '/html/body/div[1]/div[2]/table[2]/tr[' + str(i) + ']/td[3]/div/div[3]/a/@href').extract_first()
            uploader = response.xpath(
                '/html/body/div[1]/div[2]/table[2]/tr[' + str(i) + ']/td[4]/div/a/text()').extract_first()
            yield Request(url=alink, callback=self.ehentai_parse_content, meta={
                'category' : category,
                'publish' : publish,
                'name' : name,
                'alink' : alink,
                'uploader' : uploader,
                'page' : page
            })

    # 'https://e-hentai.org/g/1220311/651f311c1d/'
    def ehentai_parse_content(self, response):
        i = 3
        while (True):
            paging = response.xpath('/html/body/div[3]/table/tr/td[3]/text()').extract_first()
            if not paging :
                break
            elif paging == '>':
                break
            else:
                i += 1

        for i in range(3, i+1):
            j = 1
            while (True):
                pic_url = response.xpath('//*[@id="gdt"]/div[' + str(j) +']/div/a/@href').extract_first()
                if not pic_url:
                    break
                else:
                    meta = response.meta
                    sort = response.xpath('//*[@id="gdt"]/div[' + str(j) + ']/div/a/img/@alt').extract_first()
                    meta['sort'] = sort
                    yield Request(url = pic_url, callback = self.ehentai_parse_pic, meta=meta)
                j += 1

    def ehentai_parse_pic(self, response):
        pic_true_url = response.xpath('//*[@id="img"]/@src').extract_first()
        if not pic_true_url:
            return
        yield Request(url = pic_true_url, callback = self.ehentai_down_pic, meta=response.meta)

    def ehentai_down_pic(self, response):
        path_name = 'images/' + response.meta['name']
        img_name = response.meta['sort'] + '.jpg'
        if not os.path.exists(path_name):
            os.makedirs(path_name)

        img_stream = response.body
        file_obj = open(path_name + '/' + img_name, 'wb')
        file_obj.write(img_stream)
        file_obj.flush()
        file_obj.close()
        print('start to scrapy %s : %s' % (path_name, img_name))
        print('file download success')

    def test(self, response):
        if not os.path.exists('images/[Jora-bora] Seaside Snack'):
            a = os.makedirs('images/[Jora-bora] Seaside Snack')
            print(a)