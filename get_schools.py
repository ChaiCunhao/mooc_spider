"""
爬取大学数据
"""

import json
from os import makedirs
from os.path import exists
import requests
import logging
import re
from urllib.parse import urljoin

# 日志输出格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
# mooc主页和大学列表页url
BASE_URL = 'https://www.icourse163.org'
SCHOOLS_URL = 'https://www.icourse163.org/university/view/all.htm#/'
# 保存目录
RESULTS_DIR = 'mooc_results'
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)


def scrape_page(url):
    """
    以get方式请求页面，返回页面html代码
    :param url: page url
    :return: html of page
    """
    # logging.info('scraping %s...', url)
    try:
        response = requests.get(url)
        if response.status_code == requests.codes.ok:  # 即200
            return response.text
        logging.error('get invalid status code %s while scraping %s', response.status_code, url)
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_schools():
    """
    爬取大学列表页，返回页面html代码
    :return:
    """
    return scrape_page(SCHOOLS_URL)


def parse_schools(html):
    """
    解析大学列表页html，返回学校简略信息
    :param html:
    :return:
    """
    # 正则表达式提取 大学主页url、大学图片（列表页）、大学名称
    pattern = re.compile('<a class="u-usity f-fl" href="(.*?)".*?<img.*?src="(.*?)".*?alt="(.*?)".*?</a>', re.S)
    schools = re.findall(pattern, html)
    # 迭代返回 {大学主页url, 大学图片（列表页）, 大学名称}
    if not schools:
        return []
    for school in schools:
        school_url = urljoin(BASE_URL, school[0])
        school_img = school[1]
        school_name = school[2]
        logging.info('get url,img,name of school %s', school_name)
        yield {
            'school_name': school_name,
            'school_url': school_url,
            'school_img': school_img
        }


def scrape_school_home(url):
    """
    爬取大学主页，返回页面html代码
    :param url:
    :return:
    """
    return scrape_page(url)


def parse_school_home(html):
    """
    解析学校主页，返回学校id
    :param html: html of detail page
    :return: data
    """
    school_id_pattern = re.compile('schoolId = "(.*?)"')
    school_id = re.search(school_id_pattern, html).group(1).strip() if re.search(school_id_pattern, html) else None
    logging.info('get school id %s', school_id)
    return school_id


def save_data(data):
    """
    传入python列表或字典，保存为json文件
    :param data:
    :return:
    """
    # 构建保存路径
    data_path = f'{RESULTS_DIR}/schools.json'
    exists(f'{RESULTS_DIR}') or makedirs(f'{RESULTS_DIR}')
    # 保存为json文件
    json.dump(data, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    logging.info(f'saved {data_path}')


def main():
    """
    main process
    :return:
    """
    # 爬取大学列表页，获取 {大学主页url、大学图片（列表页）、大学名称}，装入列表
    schools_html = scrape_page(SCHOOLS_URL)
    schools_list = list(parse_schools(schools_html))
    # 获取学校id字段,装入列表
    for _ in schools_list:
        school_home_html = scrape_school_home(_['school_url'])
        school_id = parse_school_home(school_home_html)
        _['school_id'] = school_id
    # 保存信息
    save_data(schools_list)

    logging.info('data saved successfully')


if __name__ == '__main__':
    main()
