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

def login(driver, username, password):
    driver.get('https://leetcode.com/accounts/login/')
    driver.find_element_by_xpath('// *[ @ id = "id_login"]').send_keys(username)
    driver.find_element_by_xpath('// *[ @ id = "id_password"]').send_keys(password)
    driver.find_element_by_xpath('// *[ @ id = "id_password"]').send_keys(Keys.ENTER)
    time.sleep(10)
    logging.info('Login successful!')


def get_submissions(driver, args):
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

    logging.info('Crawing submissions, please wait carefully...')
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
    logging.info('Submission counts: \n{}'.format(submissions['Question'].value_counts()))
    
    submissions.to_csv(args.save_submissions_path, index=False)
    return submissions


def get_contest(driver, contest_name):
    retry = 3
    while retry:
        try:
            driver.get('https://leetcode.com/contest/' + contest_name)
            time.sleep(3)
            questions_link = []
            table = driver.find_element_by_xpath('//*[@id="contest-app"]/div/div/div[4]/div[1]/ul')
            q_list = table.find_elements_by_tag_name('li')[1:]
            for q in q_list:
                questions_link.append(q.find_element_by_tag_name('a').get_attribute('href'))
            break
        except:
            logging.info('Get contest failed, retrying...')
            retry -= 1
            driver.back()
    if retry == 0:
        logging.info('Get contest failed')
        return []
    
    try:
        logging.info('Crawing questions...')
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
    ranking_url = f'https://leetcode.com/contest/{contest_name}/ranking/'
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

    contest = [contest_name, max_par]
    for q in contest_questions:
        contest.append(q[1] / max_par)
    contest.append(np.mean(contest[2:]))
    contest_df = pd.DataFrame(contest).transpose()
    contest_df.columns = ['contest_num','total_participants','problem1','problem2','problem3','problem4','total_accepted']
    return contest_df


def get_contests(driver, args):
    contests = pd.DataFrame(columns=['contest_num','total_participants','problem1','problem2','problem3','problem4','total_accepted'])

    if os.path.isfile(args.save_path):
        contests = pd.read_csv(args.save_path)
    
    for contest_num in range(args.start, args.end+1):
        if contest_num % 2:
            bn = contest_num // 2 - 68
            contest_name = 'biweekly-contest-'+str(bn)
            if args.rewrite or contest_name not in contests['contest_num'].values:
                logging.info(contest_name)
                contest = get_contest(driver, contest_name)
                if len(contest):
                    if contest_name in contests['contest_num'].values:
                        contests[contests['contest_num']==contest_name] = contest
                    else:
                        contests = contests.append(contest)
            else:
                logging.info('{} already exsits.'.format(contest_name))
        
        contest_name = 'weekly-contest-'+str(contest_num)
        if args.rewrite or contest_name not in contests['contest_num'].values:
            logging.info(contest_name)
            contest = get_contest(driver, contest_name)
            if len(contest):
                if contest_name in contests['contest_num'].values:
                    contests[contests['contest_num']==contest_name] = contest
                else:
                    contests = contests.append(contest)
        else:
            logging.info('{} already exsits.'.format(contest_name))
    
    contests.to_csv(args.save_path,index=False,header=True)
    return contests


def post_info(driver, args):
    logging.info('loading csv file...')
    contests_df = pd.read_csv(args.save_path)

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
    driver.get(args.post_url)
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
    
    logging.info('Posting msg to discussion...')
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