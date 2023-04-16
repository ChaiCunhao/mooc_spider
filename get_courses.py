"""
爬取大学的课程数据
需在get_schools.py之后执行
"""

import multiprocessing
import requests
import logging
import json
from os import makedirs
from os.path import exists

# 日志输出格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
# url
BASE_URL = 'https://www.icourse163.org'  # mooc主页
COURSE_URL = 'https://www.icourse163.org/web/j/courseBean.getCourseListBySchoolId.rpc?csrfKey={csrfkey}'  # ajax请求url,获取大学课程
# 保存目录
RESULTS_DIR = 'mooc_results/courses'
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)


def get_csrf():
    """
    从cookie中获取csrf令牌，并返回它们
    :return:
    """
    csrf = ''
    r = requests.get(BASE_URL)
    for key, value in r.cookies.items():
        if key == 'NTESSTUDYSI':
            csrf = value
            logging.info('get csrf key')
    return r.cookies, csrf


def scrape_api(url, data, cookies):
    """
    以post方式请求url，返回json数据
    """
    # logging.info('scraping %s...', url)
    try:
        response = requests.post(url, data=data, cookies=cookies)
        if response.status_code == requests.codes.ok:  # 即200
            return response.json()
        logging.error('get invalid status code %s while scraping %s', response.status_code, url)
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_courses(school_id, page, cookies, csrf):
    """
    传入大学id，以及页码，返回该页课程的json数据
    """
    url = COURSE_URL.format(csrfkey=csrf)
    data = {
        'schoolId': school_id,  # 学校id
        'p': page,  # 页码
        'psize': 20,  # 每页的课程数
        'type': 1,  # 不详
        'courseStatus': 30,  # 课程状态：全部（正在进行、即将开始、已结束）
    }
    result = scrape_api(url, data, cookies)
    logging.info('get courses of school id %s, page %s', school_id, page)
    return result


def get_params():
    """
    生成多进程需要的参数列表
    """
    # 定义参数列表
    params = []
    # 读取schools.json文件，得到全部学校名称和学校Id，存入参数列表
    with open('mooc_results/schools.json', 'r', encoding='utf-8') as file:
        schools = json.loads(file.read())
    for school in schools[:6]:
        params.append((school['school_name'], school['school_id']))
    return params


def save_data(data):
    """
    保存数据为json文件
    """
    # 获取学校名，将斜杠替换，防止路径歧义
    school_name = data.get('school_name').replace('/', '／').replace('\\', '＼')
    # 构建保存路径
    data_path = f'{RESULTS_DIR}/courses_of_{school_name}.json'
    exists(f'{RESULTS_DIR}') or makedirs(f'{RESULTS_DIR}')
    # 保存为json文件
    json.dump(data, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    logging.info(f'saved {data_path}')


def main(school_name, school_id):
    """
    爬取一所大学的全部课程，保存为json文件
    :param school_name:
    :param school_id:
    :return:
    """
    # 定义课程列表
    courses = []
    # 获取cookie和csrf令牌
    cookies, csrf = get_csrf()
    # 爬取第一页课程
    first_data = scrape_courses(school_id, 1, cookies, csrf)
    # 得到该大学总课程数和总课程页数
    totle_count = int(first_data['result']['query']['totleCount'])
    totle_page_count = int(first_data['result']['query']['totlePageCount'])
    # 将课程存入课程列表
    if totle_count != 0:
        # 将第一页课程存入课程列表
        for course in first_data['result']['list']:
            courses.append(course)
        # 爬取其余页的课程，并存入课程列表
        for i in range(2, totle_page_count + 1):
            data = scrape_courses(school_id, i, cookies, csrf)
            for course in data['result']['list']:
                courses.append(course)
    # 保存为json文件
    school_courses = {
        'school_name': school_name,
        'school_id': school_id,
        'courses_count': totle_count,
        'school_courses': courses
    }
    save_data(school_courses)


if __name__ == '__main__':
    # 生成参数列表
    params = get_params()
    # 打印进程数（即cpu核数）
    print("Number of processers: ", multiprocessing.cpu_count())
    # 多进程爬取
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    # pool.map(main,)
    pool.starmap(main, params)  # 维持执行的进程总数为[计算机cpu核数]，当一个进程执行完毕后会添加新的进程进去
    pool.close()  # 执行完close后不会有新的进程加入到pool
    pool.join()  # 主进程阻塞，等待所有子进程的退出
