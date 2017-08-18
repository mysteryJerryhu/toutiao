# -*- coding: UTF-8 -*-
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
from bs4 import BeautifulSoup
import requests
import urllib3
import re
# from config import *
import pymongo
import os
from hashlib import md5
from json.decoder import JSONDecodeError
from multiprocessing import Pool

#client=pymongo.MongoClient(MONGO_URL,connect=False)
#db=client[MONGO_DB]

def get_page_index(offset,keyword):
    date={
        'offset':offset,
        'format':'json',
        'keyword':keyword,
        'autoload':'true',
        'count':'20',
        'cur_tab':3
    }
    url='https://www.toutiao.com/search_content/?'+urlencode(date)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('error')
        return None


def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')


def get_page_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('error', url)
        return None


def parase_page_details(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    print(title)
    images_pattern = re.compile('gallery=(.*?);', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.load(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for images in images: download_image(images)
            return {
                'title': title,
                'url': url,
                'images': images
            }


def download_image(url):
    print('download', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_to_mongo(response.content)
        return None
    except RequestException:
        print('error', url)
        return None


def save_image(content):
    file_path = '{0}/{1},{2}'.format(os.getcwd(), md5(content), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def save_to_mongo(result):
    #if db[MONGO_TABLE].insert(result):
        print('success', result)
       # return True
    #return False


def main(offset):
    html = get_page_index(offset, '街拍')
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parase_page_details(html, url)
            print(result)
            # if result: save_to_mongo(result)


if __name__ == '__main__':
    group = [x * 20 for x in range(1, 20)]
    pool = Pool()
    pool.map(main, group)

