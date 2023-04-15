import json
from os import makedirs
from os.path import exists
import requests
import logging
import re
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'https://www.icourse163.org'
SCHOOLS_URL = 'https://www.icourse163.org/university/view/all.htm#/'

RESULTS_DIR = 'mooc_results'
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)


def scrape_page(url):
    """
    以get方式请求页面，返回页面代码
    :param url: page url
    :return: html of page
    """
    logging.info('scraping %s...', url)
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
    解析大学列表页，返回学校简略信息
    :param html:
    :return:
    """
    pattern = re.compile('<a class="u-usity f-fl" href="(.*?)".*?<img.*?src="(.*?)".*?alt="(.*?)".*?</a>', re.S)
    schools = re.findall(pattern, html)
    if not schools:
        return []
    for school in schools:
        school_url = urljoin(BASE_URL, school[0])
        school_img = school[1]
        school_name = school[2]
        logging.info('get  detail url of school %s', school_name)
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
    解析学校主页，获取学校id
    :param html: html of detail page
    :return: data
    """

    school_id_pattern = re.compile('schoolId = "(.*?)"')
    school_id = re.search(school_id_pattern, html).group(1).strip() if re.search(school_id_pattern, html) else None
    return school_id


def save_data(data):
    """
    传入python列表或字典，保存为json文件
    :param data:
    :return:
    """
    data_path = f'{RESULTS_DIR}/schools.json'
    json.dump(data, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def main(url):
    """
    main process
    :return:
    """
    schools_html = scrape_page(url)
    schools_list = list(parse_schools(schools_html))
    for _ in schools_list:
        school_home_html = scrape_school_home(_['school_url'])
        school_id = parse_school_home(school_home_html)
        _['school_id'] = school_id
    save_data(schools_list)
    logging.info('data saved successfully')


if __name__ == '__main__':
    main(SCHOOLS_URL)
