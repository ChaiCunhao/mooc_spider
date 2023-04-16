"""
爬取课程下的评论数据
需在get_courses.py之后执行
"""

import multiprocessing
import requests
import logging
import json
from os import makedirs
from os.path import exists
import os

# 日志输出格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
# url
BASE_URL = 'https://www.icourse163.org'  # mooc主页
COURSE_URL = 'https://www.icourse163.org/web/j/mocCourseV2RpcBean.getCourseEvaluatePaginationByCourseIdOrTermId.rpc?csrfKey={csrfkey}'  # ajax请求url,获取大学课程评论
# 保存目录
RESULTS_DIR = 'mooc_results/comments'
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


def scrape_comments(course_id, page_index, cookies, csrf):
    """
    传入课程id，以及页码，返回该页课程评论的json数据
    """
    url = COURSE_URL.format(csrfkey=csrf)
    data = {
        'courseId': course_id,  # 课程id
        'pageIndex': page_index,  # 页码
        'pageSize': 20,  # 每页的评论数
        'orderBy': 3,  # 排序（3代表的排序依据不详）
    }
    result = scrape_api(url, data, cookies)
    logging.info('get comments of course id %s, page %s', course_id, page_index)
    return result


def getfiles(dir):
    """
    返回目标路径下的文件和文件夹的名字列表
    """
    filenames = os.listdir(f'{dir}')
    return filenames


def get_params():
    """
    生成多进程需要的参数列表
    """
    # 定义参数列表
    params = []
    # 获取课程文件名列表
    course_files = getfiles('mooc_results/courses')
    # 读取全部课程文件，得到全部学校名称、课程名称和课程Id，存入参数列表
    for course_file in course_files:
        with open(f'mooc_results/courses/{course_file}', 'r', encoding='utf-8') as file:
            courses = json.loads(file.read())
        school_name = courses['school_name']
        for course in courses['school_courses']:
            params.append((school_name, course['name'], course['id']))
    return params


def save_data(data):
    """
    保存数据为json文件
    """
    # 获取学校名和课程名，将斜杠替换，防止路径歧义
    school_name = data.get('school_name').replace('/', '／').replace('\\', '＼')
    course_name = data.get('course_name').replace('/', '／').replace('\\', '＼')
    # 构建保存路径
    data_path = f'{RESULTS_DIR}/{school_name}/comments_of_{course_name}.json'
    exists(f'{RESULTS_DIR}/{school_name}') or makedirs(f'{RESULTS_DIR}/{school_name}')
    # 保存为json文件
    json.dump(data, open(rf'{data_path}', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    logging.info(f'saved {data_path}')


def main(school_name, course_name, course_id):
    """
    爬取一门课程的全部评论，保存为json文件
    """
    # 定义评论列表
    comments = []
    # 获取cookie和csrf令牌
    cookies, csrf = get_csrf()
    # 爬取第一页评论
    first_data = scrape_comments(course_id, 1, cookies, csrf)
    # 得到该课程总评论数和总评论页数
    totle_count = int(first_data['result']['query']['totleCount'])
    totle_page_count = int(first_data['result']['query']['totlePageCount'])
    # 将课程评论存入评论列表
    if totle_count != 0:
        # 将第一页评论存入评论列表
        for comment in first_data['result']['list']:
            comments.append(comment)
        # 爬取其余页的评论，并存入评论列表
        for i in range(2, totle_page_count + 1):
            data = scrape_comments(course_id, i, cookies, csrf)
            for comment in data['result']['list']:
                comments.append(comment)
    # 保存为json文件
    course_comments = {
        'school_name': school_name,
        'course_name': course_name,
        'course_id': course_id,
        'comments_count': totle_count,
        'course_comments': comments
    }
    save_data(course_comments)


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
