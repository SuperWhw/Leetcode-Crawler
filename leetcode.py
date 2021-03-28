import os
import time
import json
import requests
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
TIME_DELAY = 10
logging.basicConfig(level=logging.INFO)

driver_path = r"D:\Chrome Downloads\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--incognito')
# chrome_options.add_argument('--headless')
driver = webdriver.Chrome(driver_path,options=chrome_options)
driver.implicitly_wait(TIME_DELAY)

def login(driver, username, password):
    driver.get('https://leetcode.com/accounts/login/')
    driver.find_element_by_xpath('// *[ @ id = "id_login"]').send_keys(username)
    driver.find_element_by_xpath('// *[ @ id = "id_password"]').send_keys(password)
    driver.find_element_by_xpath('// *[ @ id = "id_password"]').send_keys(Keys.ENTER)
    time.sleep(10)
    logging.info('Login successful!')

def get_submissions(driver, save=False, save_path='submission.csv'):
    driver.get('https://leetcode.com/submissions/')
    submissions = []
    header = []
    body = []
    table = driver.find_element_by_xpath('//*[@id="submission-list-app"]/div/table')
    thead = table.find_element_by_tag_name('thead')
    for row in thead.find_elements_by_tag_name('tr'):
        for col in row.find_elements_by_tag_name('th'):
            header.append(col.text)
    header += ['Link']

    while True:
        table = driver.find_element_by_xpath('//*[@id="submission-list-app"]/div/table')
        tbody = table.find_element_by_tag_name('tbody')
        for row in tbody.find_elements_by_tag_name('tr'):
            row_list = row.find_elements_by_tag_name('td')
            body.append([col.text for col in row_list] + [row_list[2].find_element_by_tag_name('a').get_attribute('href')])
        try:
            next_button = driver.find_element_by_xpath('//*[@id="submission-list-app"]/div/nav/ul/li[2]/a')
        except NoSuchElementException:
            break
        next_button.click()
    submissions = pd.DataFrame(body, columns=header)

    logging.info('Problems done: {}'.format(submissions['Question'].nunique()))
    logging.info('Submission counts: {}'.format(submissions['Question'].value_counts()))
    
    if save:
        submissions.to_csv(save_path,index=False)
    return submissions

def get_contest(driver, contest_cate, contest_num):
    retry = 3
    while retry:
        try:
            driver.get('https://leetcode.com/contest/' + contest_cate + '-' + str(contest_num))
            time.sleep(3)
            questions_link = []
            table = driver.find_element_by_xpath('//*[@id="contest-app"]/div/div/div[4]/div[1]/ul')
            q_list = table.find_elements_by_tag_name('li')[1:]
            for q in q_list:
                questions_link.append(q.find_element_by_tag_name('a').get_attribute('href'))
            break
        except:
            logging.info('get contest failed, retrying...')
            retry -= 1
            driver.back()
    if retry == 0:
        logging.info('get contest failed')
        return []
    
    try:
        logging.info('crawing questions...')
        contest_questions = []
        for i,ql in enumerate(questions_link):
            driver.get(ql)
            time.sleep(1)
            title = driver.find_element_by_xpath('//*[@id="base_content"]/div[1]/div/div/div[1]/h3/span').text
            table = driver.find_element_by_xpath('//*[@id="base_content"]/div[1]/div/div/div[3]/div/div[1]/ul')
            logging.info(f'[q{i}] crawing quesion {i}...')
            q_data = []
            for row in table.find_elements_by_tag_name('li')[:-1]:
                data_str = row.find_element_by_tag_name('span').text
                q_data.append(int(data_str))
            contest_questions.append([title] + q_data)
    except:
        logging.info('crawing questions failed')
        return []
    
    logging.info('get total participants...')
    ranking_url = f'https://leetcode.com/contest/{contest_cate}-{contest_num}/ranking/'
    driver.get(ranking_url)
    time.sleep(5)
    max_page = 0
    nav = driver.find_element_by_xpath('//*[@id="contest-app"]/div/div/nav/ul')
    for p in nav.find_elements_by_tag_name('li'):
        try:
            num = p.text
            if num.isdigit():
                max_page = max(max_page, int(num))
        except:
            continue

    driver.get(ranking_url + str(max_page))
    time.sleep(10)
    table = driver.find_element_by_xpath('//*[@id="contest-app"]/div/div/div[2]/div[2]/table')
    tbody = table.find_element_by_tag_name('tbody')
    last_row = tbody.find_elements_by_tag_name('tr')[-1]
    max_par = int(last_row.find_element_by_tag_name('td').text)
    logging.info(f'got participants: {max_par}')

    # contest_questions = pd.DataFrame(contest_questions, columns=['Question','User Accepted','User Tried','Total Accepted','Total Submissions'])
    # contest_questions['Total Accepted Rate'] = contest_questions['Total Accepted'] / contest_questions['Total Submissions']
    # contest_questions['User Accepted Rate'] = contest_questions['User Accepted'] / max_par

    contest_str = str(contest_num) if contest_cate=='weekly-contest' else 'b'+str(contest_num)
    contest = [contest_str, max_par]
    for q in contest_questions:
        contest.append(q[1] / max_par)
    contest.append(np.mean(contest[2:]))
    return contest

def get_contests(start=200,end=0,save_path='contests_info.csv',bi_pass=False):

    contests = []
    for contest_num in range(start,end+1):
        if contest_num % 2 and not bi_pass:
            bn = contest_num // 2 - 68
            logging.info(f'biweekly contest #{bn}')
            contest = get_contest(driver,'biweekly-contest',bn)
            if contest: contests.append(contest)
            
        logging.info(f'weekly contest #{contest_num}')
        contest = get_contest(driver,'weekly-contest', contest_num)
        if contest: contests.append(contest)
    contests_df = pd.DataFrame(contests, columns=['contest_num','total_participants','problem1','problem2','problem3','problem4','total_accepted'])
    
    if os.path.isfile(save_path):
        ori_df = pd.read_csv(save_path)
        for i in range(len(contests_df)):
            row = contests_df.iloc[i].to_list()
            if row[0] in ori_df['contest_num'].values:
                ori_df[ori_df['contest_num']==row[0]] = row
            else:
                ori_df.append(row)
        contests_df = ori_df
        del ori_df
    
    contests_df.to_csv('contests_info.csv',index=False,header=True)
    return contests_df

def post_info(url,csv_path='contests_info.csv',post=True):
    logging.info('loading csv file...')
    contests_df = pd.read_csv(csv_path)

    cur_contest = contests_df.iloc[-1,:]
    tot_par = cur_contest[1]

    contests_df = contests_df.iloc[:-1,:]

    # difficulty = ''
    # if abs(cur_contest[6] - contests_df['total_accepted'].mean()) < 0.02:
    #     difficulty = 'similar to'
    # elif cur_contest[6] < contests_df['total_accepted'].mean():
    #     difficulty = 'harder than'
    # else:
    #     difficulty = 'easier than'

    logging.info('generating contest msg...')
    driver.get(url)
    time.sleep(5)
    msg = f"There are **{int(tot_par)}** participants.\n" + \
        "|  Problem Num | Ac Rate | Avg Ac Rate* |\n" + \
        "|  ----  | ----  | ----  |\n" + \
        "| Problem1 | {:.2f}% | {:.2f}% |\n".format(cur_contest[2]*100,contests_df['problem1'].mean()*100) + \
        "| Problem2 | {:.2f}% | {:.2f}% |\n".format(cur_contest[3]*100,contests_df['problem2'].mean()*100) + \
        "| Problem3 | {:.2f}% | {:.2f}% |\n".format(cur_contest[4]*100,contests_df['problem3'].mean()*100) + \
        "| Problem4 | {:.2f}% | {:.2f}% |\n".format(cur_contest[5]*100,contests_df['problem4'].mean()*100) + \
        "| Total | {:.2f}% | {:.2f}% |\n".format(cur_contest[6]*100,contests_df['total_accepted'].mean()*100) + \
        "> \\* Count from Weekly-Contest 200\n" + \
        "> For more details, please see https://1drv.ms/x/s!AmUyLy2gP9TnpTZpPGxr7iAHAU9a?e=bngZEt. (System may have delay, please refer to the actual situation)"
    print(msg)
    if post:
        logging.info('posting msg to discussion...')
        driver.find_element_by_xpath('//*[@id="discuss-container"]/div/div/div/div[2]/div[2]/div[2]/div[1]/div/div[1]/textarea').send_keys(msg)
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="discuss-container"]/div/div/div/div[2]/div[2]/div[2]/div[1]/div/div[2]/button').click()
        logging.info('Successful posted!')

if __name__ == '__main__':
    login(username='', password='')
    # get_submissions()
    # contests_df = get_contests(start=229,end=230)  # crawing from start to end
    contests_df = get_contests(231) # crawing biweekly contest
    # contests_df = get_contests(230, bi_pass=True) # crawing weekly contest
    post_info(url='https://leetcode.com/discuss/general-discussion/1096244/biweekly-contest-47')
    driver.close()