#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: juzipi
@file: spider_data.py
@time:2022/07/20
@description:
"""

import requests
import pymongo
from lxml import etree
import tqdm
from utils.config import SysConfig


class MedicineSpider(object):
    __doc__ = """ 医药数据爬取 """

    def __init__(self):
        self.mongodb_con = pymongo.MongoClient(host=SysConfig.MONGODB_HOST, port=SysConfig.MONGODB_PORT)
        self.db = self.mongodb_con['medicine']
        self.col = self.db['data']

    @staticmethod
    def get_html(url):
        """
        爬取url对应内容
        :param url: 连接
        :return: 页面内容
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        html = requests.get(url=url, headers=headers).content.decode("gbk")
        return html

    def inspect_crawl(self):
        for page in range(1, 3685):
            try:
                url = 'http://jck.xywy.com/jc_%s.html' % page
                html = self.get_html(url)
            except Exception as e:
                print(f'requests error, {e}')

    def spider_data(self):
        """
        爬取数据主程序入口
        :return:
        """
        for page in tqdm.tqdm(range(1, 11000), desc="crawling"):
            try:
                # build data url
                basic_url = 'http://jib.xywy.com/il_sii/gaishu/%s.htm' % page
                cause_url = 'http://jib.xywy.com/il_sii/cause/%s.htm' % page
                prevent_url = 'http://jib.xywy.com/il_sii/prevent/%s.htm' % page
                symptom_url = 'http://jib.xywy.com/il_sii/symptom/%s.htm' % page
                inspect_url = 'http://jib.xywy.com/il_sii/inspect/%s.htm' % page
                treat_url = 'http://jib.xywy.com/il_sii/treat/%s.htm' % page
                food_url = 'http://jib.xywy.com/il_sii/food/%s.htm' % page
                drug_url = 'http://jib.xywy.com/il_sii/drug/%s.htm' % page
                data = {}
                data['url'] = basic_url
                data['basic_info'] = self.basic_info_spider(basic_url)
                data['cause_info'] = self.common_spider(cause_url)
                data['prevent_info'] = self.common_spider(prevent_url)
                data['symptom_info'] = self.symptom_spider(symptom_url)
                data['inspect_info'] = self.inspect_spider(inspect_url)
                data['treat_info'] = self.treat_spider(treat_url)
                data['food_info'] = self.food_spider(food_url)
                data['drug_info'] = self.drug_spider(drug_url)
                print(page, basic_url)
                print(data)
                exit()
                self.col.insert(data)
            except Exception as e:
                print(e, page)
        return

    def basic_info_spider(self, url):
        """
        概述内容爬取
        :param url: 爬取链接
        :return:
        """
        html = self.get_html(url)
        selector = etree.HTML(html)
        title = selector.xpath('//title/text()')[0]  # 基本名称
        category = selector.xpath('//div[@class="wrap mt10 nav-bar"]/a/text()')  # 疾病类别
        desc = selector.xpath('//div[@class="jib-articl-con jib-lh-articl"]/p/text()')  # 疾病描述
        ps = selector.xpath('//div[@class="mt20 articl-know"]/p')  # 基本属性
        info_box = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ',
                                                                                                        '').replace(
                '\t', '')
            info_box.append(info)
        basic_data = {}
        basic_data['category'] = category
        basic_data['name'] = title.split('的简介')[0]
        basic_data['desc'] = desc
        basic_data['attributes'] = info_box
        return basic_data

    def common_spider(self, url):
        """
        通用数据爬取
        :param url:
        :return:
        """
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//p')
        info_box = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ',
                                                                                                        '').replace(
                '\t', '')
            if info:
                info_box.append(info)
        return '\n'.join(info_box)

    def symptom_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        symptoms = selector.xpath('//a[@class="gre" ]/text()')
        ps = selector.xpath('//p')
        detail = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ',
                                                                                                        '').replace(
                '\t', '')
            detail.append(info)
        symptoms_data = {}
        symptoms_data['symptoms'] = symptoms
        symptoms_data['symptoms_detail'] = detail
        return symptoms, detail

    def inspect_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        inspects  = selector.xpath('//li[@class="check-item"]/a/@href')
        return inspects

    def treat_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//div[starts-with(@class,"mt20 articl-know")]/p')
        infobox = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            infobox.append(info)
        return infobox

    def drug_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        drugs = [i.replace('\n','').replace('\t', '').replace(' ','') for i in selector.xpath('//div[@class="fl drug-pic-rec mr30"]/p/a/text()')]
        return drugs

    def food_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        divs = selector.xpath('//div[@class="diet-img clearfix mt20"]')
        try:
            food_data = {}
            food_data['good'] = divs[0].xpath('./div/p/text()')
            food_data['bad'] = divs[1].xpath('./div/p/text()')
            food_data['recommend_eat'] = divs[2].xpath('./div/p/text()')
        except:
            return {}
        return food_data
