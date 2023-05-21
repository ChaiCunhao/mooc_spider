"""
爬取评论者的个人主页信息
需在get_course_comments.py之后执行
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
USER_BASE_URL = 'https://www.icourse163.org/web/j/memberBean.getMocMemberPersonalDtoById.rpc?csrfKey={csrfkey}'  # ajax请求url,获取用户基本信息
USER_LEARNED_COURSES_URL = 'https://www.icourse163.org/web/j/learnerCourseRpcBean.getOtherLearnedCoursePagination.rpc?csrfKey={csrfkey}'  # ajax请求url,获取用户学习过的课程
USER_POST_URL = 'https://www.icourse163.org/web/j/MocPostRpcBean.getPostByUserId.rpc?csrfKey={csrfkey}'  # ajax请求url,获取用户发表的主题
USER_REPLY_URL = 'https://www.icourse163.org/web/j/MocPostRpcBean.getReplyByUserId.rpc?csrfKey={csrfkey}'  # ajax请求url,获取用户发表的回复
USER_COMMENT_URL = 'https://www.icourse163.org/web/j/MocPostRpcBean.getCommentByUserId.rpc?csrfKey={csrfkey}'  # ajax请求url,获取用户发表的评论


# 保存目录
RESULTS_DIR = 'mooc_results/user_info'
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

def scrape_user_base_info(user_id, cookies, csrf):
    """
    传入用户id，返回该用户基本信息的json数据
    """
    url = USER_BASE_URL.format(csrfkey=csrf)
    data = {
        'memberId': user_id,  # 用户id
    }
    result = scrape_api(url, data, cookies)
    if result['code'] == 0:
        logging.info('get base_info of user id %s', user_id)
    else:
        logging.error('get invalid result while scraping base_info of user id %s', user_id)
    return result['result']

def scrape_user_learned_courses(user_id, cookies, csrf):
    """
    传入用户id，返回该用户学习过的课程的json数据
    """
    #初始化返回数据
    user_learned_courses=[]
    totle_count = 0
    totle_page_count = 0
    #先爬取第一页数据，获取总页数
    url = USER_LEARNED_COURSES_URL.format(csrfkey=csrf)
    data = {
        'uid': user_id,  # 用户id
        'pageIndex': 1,  # 页码
        'pageSize': 32,  # 每页主题数
    }
    first_data = scrape_api(url, data, cookies)
    if first_data['code'] == 0:
        totle_count = int(first_data['result']['query']['totleCount'])#总课程数
        totle_page_count = int(first_data['result']['query']['totlePageCount'])#总页数
        if totle_count > 0:
            # 保存第一页数据
            user_learned_courses.extend(first_data['result']['list'])
            # 爬取剩余页数据
            for page in range(2, totle_page_count + 1):
                data['pageIndex'] = page
                result = scrape_api(url, data, cookies)
                if result['code'] == 0:
                    user_learned_courses.extend(result['result']['list'])
                else:
                    logging.error('get invalid result while scraping courses of user id %s', user_id)
        logging.info('get courses of user id %s', user_id)
    else:
        logging.error('get invalid result while scraping courses of user id %s', user_id)

    return {'totle_count': totle_count, 'totle_page_count': totle_page_count, 'user_learned_courses': user_learned_courses}

def scrape_user_post(user_id, cookies, csrf):
    """
    传入用户id，返回该用户发表的主题的json数据
    """
    #初始化返回数据
    user_post=[]
    totle_count = 0
    totle_page_count = 0
    #先爬取第一页数据，获取总页数
    url = USER_POST_URL.format(csrfkey=csrf)
    data = {
        'userId': user_id,  # 用户id
        'p': 1,  # 页码
        'psize': 20,  # 每页主题数
        'isOfficerPage': 0
    }
    first_data = scrape_api(url, data, cookies)
    if first_data['code'] == 0:
        totle_count = int(first_data['result']['pagination']['totleCount'])#总主题数
        totle_page_count = int(first_data['result']['pagination']['totlePageCount'])#总页数
        if totle_count > 0:
            # 保存第一页数据
            user_post.extend(first_data['result']['postsList'])
            # 爬取剩余页数据
            for page in range(2, totle_page_count + 1):
                data['p'] = page
                result = scrape_api(url, data, cookies)
                if result['code'] == 0:
                    user_post.extend(result['result']['postsList'])
                else:
                    logging.error('get invalid result while scraping post of user id %s', user_id)
        logging.info('get post of user id %s', user_id)
    else:
        logging.error('get invalid result while scraping post of user id %s', user_id)

    return {'totle_count': totle_count, 'totle_page_count': totle_page_count, 'user_post': user_post}

def scrape_user_reply(user_id, cookies, csrf):
    """
    传入用户id，返回该用户发表的回复的json数据
    """
    #初始化返回数据
    user_reply=[]
    totle_count = 0
    totle_page_count = 0
    #先爬取第一页数据，获取总页数
    url = USER_REPLY_URL.format(csrfkey=csrf)
    data = {
        'userId': user_id,  # 用户id
        'p': 1,  # 页码
        'psize': 20,  # 每页主题数
        'isOfficerPage':0
    }
    first_data = scrape_api(url, data, cookies)
    if first_data['code'] == 0:
        totle_count = int(first_data['result']['pagination']['totleCount'])#总主题数
        totle_page_count = int(first_data['result']['pagination']['totlePageCount'])#总页数
        if totle_count > 0:
            # 保存第一页数据
            user_reply.extend(first_data['result']['replyList'])
            # 爬取剩余页数据
            for page in range(2, totle_page_count + 1):
                data['p'] = page
                result = scrape_api(url, data, cookies)
                if result['code'] == 0:
                    user_reply.extend(result['result']['replyList'])
                else:
                    logging.error('get invalid result while scraping reply of user id %s', user_id)
        logging.info('get reply of user id %s', user_id)
    else:
        logging.error('get invalid result while scraping reply of user id %s', user_id)

    return {'totle_count': totle_count, 'totle_page_count': totle_page_count, 'user_reply': user_reply}

def scrape_user_comments(user_id, cookies, csrf):
    """
    传入用户id，返回该用户发表的评论的json数据
    """
    #初始化返回数据
    user_comments=[]
    totle_count = 0
    totle_page_count = 0
    #先爬取第一页数据，获取总页数
    url = USER_COMMENT_URL.format(csrfkey=csrf)
    data = {
        'userId': user_id,  # 用户id
        'p': 1,  # 页码
        'psize': 20,  # 每页主题数
        'isOfficerPage':0,
    }
    first_data = scrape_api(url, data, cookies)
    if first_data['code'] == 0:
        totle_count = int(first_data['result']['pagination']['totleCount'])#总评论数
        totle_page_count = int(first_data['result']['pagination']['totlePageCount'])#总页数
        if totle_count > 0:
            # 保存第一页数据
            user_comments.extend(first_data['result']['commentList'])
            # 爬取剩余页数据
            for page in range(2, totle_page_count + 1):
                data['pageIndex'] = page
                result = scrape_api(url, data, cookies)
                if result['code'] == 0:
                    user_comments.extend(result['result']['commentList'])
                else:
                    logging.error('get invalid result while scraping comments of user id %s', user_id)
        logging.info('get comments of user id %s', user_id)
    else:
        logging.error('get invalid result while scraping comments of user id %s', user_id)

    return {'totle_count': totle_count, 'totle_page_count': totle_page_count, 'user_comments': user_comments}



def getfiles(dir):
    """
    返回目标路径下的文件和文件夹的名字列表
    """
    filenames = os.listdir(f'{dir}')
    return filenames

def get_course_comments_files():
    """
    获得所有 课程评论文件 的路径，将以课程为单位进行多进程爬取
    """
    # 定义参数列表
    result = []
    # 获取 评论文件夹 下的 学校文件夹 名称列表
    school_dirs = getfiles('mooc_results/comments')
    for school_dir in school_dirs:
        # 获取 学校文件夹 下的 课程评论文件 名称列表
        file_names = getfiles(f'mooc_results/comments/{school_dir}')
        for file_name in file_names:
            result.append((school_dir, file_name))
    return result

def save_data(datas):
    """
    保存数据为json文件
    """
    # 获取用户ID
    user_id = datas['base_info']['result']['memberId']

    # 构建保存路径
    base_path = f'{RESULTS_DIR}/{user_id}/base_info.json'
    post_path = f'{RESULTS_DIR}/{user_id}/post.json'
    course_path = f'{RESULTS_DIR}/{user_id}/courses.json'
    reply_path = f'{RESULTS_DIR}/{user_id}/reply.json'
    comment_path = f'{RESULTS_DIR}/{user_id}/comment.json'
    # 判断文件夹是否存在，不存在则创建
    exists(f'{RESULTS_DIR}/{user_id}') or makedirs(f'{RESULTS_DIR}/{user_id}')

    # 保存为json文件
    json.dump(datas['base_info'], open(rf'{base_path}', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(datas['user_post'], open(rf'{post_path}', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(datas['user_learned_courses'], open(rf'{course_path}', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(datas['user_reply'], open(rf'{reply_path}', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(datas['user_comments'], open(rf'{comment_path}', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    logging.info(f'saved info of user id {user_id}')

def main(user_id):
    """
    爬取一个用户的全部信息，保存为json文件
    """
    # 获取csrf令牌
    cookies, csrf = get_csrf()
    # 爬取该用户基本信息
    base_info = scrape_user_base_info(user_id, cookies, csrf)
    # 爬取该用户学习过的课程
    user_learned_courses = scrape_user_learned_courses(user_id, cookies, csrf)
    # 爬取该用户发表的主题
    user_post = scrape_user_post(user_id, cookies, csrf)
    # 爬取该用户的回复
    user_reply = scrape_user_reply(user_id, cookies, csrf)
    # 爬取该用户发表的评论
    user_comments = scrape_user_comments(user_id, cookies, csrf)

    # 合并数据
    data={
        'base_info':base_info,
        'user_learned_courses': user_learned_courses,
        'user_post':user_post,
        'user_reply':user_reply,
        'user_comments':user_comments,
    }
    # 保存该用户信息
    save_data(data)

if __name__ == '__main__':

    # 打印进程数（即cpu核数）
    print("Number of processers: ", multiprocessing.cpu_count())
    # 多进程爬取
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    # 获取所有 课程评论文件 的路径
    course_comments_files = get_course_comments_files()
    # 遍历所有 课程评论文件 的路径(没有一次性读取所有文件的评论者ID，而是以课程为单位读取，防止内存溢出)
    for course_comments_file in course_comments_files:
        school_dir, file_name = course_comments_file
        logging.info('start scraping userinfo of course %s', file_name)
        # 定义该课程下的评论者id列表
        commentators = []
        # 获取该课程下的评论者id列表（以课程为单位执行多进程任务，以用户ID为单位执行单进程任务）
        with open(f'mooc_results/comments/{school_dir}/{file_name}', 'r', encoding='utf-8') as f:
            course_comments = json.load(f)
            if int(course_comments['comments_count']) > 0:
                for course_comment in course_comments['course_comments']:
                    commentators.append(course_comment['commentorId'])
        if len(commentators)>0:
            pool.map(main, commentators)  # 维持执行的进程总数为[计算机cpu核数]，当一个进程执行完毕后会添加新的进程进去

    pool.close()  # 执行完close后不会有新的进程加入到pool
    pool.join()  # 主进程阻塞，等待所有子进程的退出