import itertools
import multiprocessing
import requests
import logging
import json
from os import makedirs
from os.path import exists

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'https://www.icourse163.org'
COURSE_URL = 'https://www.icourse163.org/web/j/courseBean.getCourseListBySchoolId.rpc?csrfKey={csrfkey}'

RESULTS_DIR = 'mooc_results\schools'
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)


def get_csrf():
    csrf=''
    r = requests.get(BASE_URL)
    for key,value in r.cookies.items():
        if key=='NTESSTUDYSI':
            csrf=value
    return r.cookies,csrf


def scrape_api(url, data,cookies):
    """
    以post方式请求url，获取课程数据
    """
    logging.info('scraping %s...', url)
    try:
        response = requests.post(url, data=data,cookies=cookies)
        if response.status_code == requests.codes.ok:  # 即200
            return response.json()
        logging.error('get invalid status code %s while scraping %s', response.status_code, url)
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_courses(school_id, page,cookies,csrf):
    """
    爬取课程信息
    """
    url = COURSE_URL.format(csrfkey=csrf)
    # headers = {
    #     'cookie': 'EDUWEBDEVICE=8913c3289dc94e93b3239defff59e428; videoVolume=0.8; hasVolume=true; videoResolutionType=3; __yadk_uid=g8gXtBabON9e9ykpQfpn74M3aHvCuu23; NTESSTUDYSI=29a58f1f0eae4f22aeea18fb44ba7839; Hm_lvt_77dc9a9d49448cf5e629e5bebaa5500b=1678408564,1678945908,1680226583,1680330953; hb_MA-A976-948FFA05E931_source=www.icourse163.org; WM_NI=9oyBP%2F8tmRbEFJkzXxolSqQo3UxWXkGZbmwYae69idpxksCx51RkRENShZ7%2FtLvjnMav%2Fx6HszPMFuV%2Fkm41Kr43r79%2Bx%2FImY6y1alL5yeRz7gCN63sb%2B9MOuPOlp%2B2JcTY%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8bf47a9387c0d6ee5daeef8bb7d44f838e9a83c56ef4aba094c166f5efaba6c72af0fea7c3b92afbb1b7a3d325fcaca3b3e14f8696a59bdb74adb49d92d465f18bb8b8db618586ae8ef653a3bbfadaec70b4a8a594c274f7ef9e8cd14f8e8da8bbb625b894ba8bed47a3aae199b544b1a6a0aec57f96f1a58eb73b89aefcd4f13dfbf5b8d0cc679beab7d2e46890ebb786d172f5b98dafb539b1bee5dad045b790818df321f296adb5dc37e2a3; WM_TID=pnMNGGNxqv1AAEFRVAeVOluP4An%2BgbVW; Hm_lpvt_77dc9a9d49448cf5e629e5bebaa5500b=1680351529',
    # }
    data = {
        'schoolId': school_id,  # 学校id
        'p': page,  # 页码
        'psize': 20,  # 每页的课程数
        'type': 1,  # 不详
        'courseStatus': 30,  # 课程状态：全部（正在进行、即将开始、已结束）
    }
    return scrape_api(url, data,cookies)


def save_data(data):
    name = data.get('school_name')
    data_path = f'{RESULTS_DIR}/{name}.json'
    json.dump(data, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def main(school_name, school_id):
    courses = []
    cookies,csrf=get_csrf()
    first_data = scrape_courses(school_id, 1,cookies,csrf)
    totle_count = int(first_data['result']['query']['totleCount'])
    totle_page_count = int(first_data['result']['query']['totlePageCount'])
    for course in first_data['result']['list']:
        courses.append(course)
    for i in range(2, totle_page_count + 1):
        data = scrape_courses(school_id, i,cookies,csrf)
        for course in data['result']['list']:
            courses.append(course)
    school_courses = {
        'school_name': school_name,
        'school_id': school_id,
        'courses_count': totle_count,
        'school_courses': courses
    }
    save_data(school_courses)


if __name__ == '__main__':
    params = []
    with open('mooc_results/schools.json', 'r', encoding='utf-8') as file:
        schools = json.loads(file.read())
    for school in schools[:6]:
        params.append((school['school_name'], school['school_id']))
    pool = multiprocessing.Pool()
    # pool.map(main,)
    pool.starmap(main, params)
    pool.close()
