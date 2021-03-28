import os
import time
import json
import argparse
import requests
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from leetcode import *

TIME_DELAY = 10
logging.basicConfig(level=logging.INFO)

driver_path = r"D:\Chrome Downloads\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--incognito')
# chrome_options.add_argument('--headless')
driver = webdriver.Chrome(driver_path,options=chrome_options)
driver.implicitly_wait(TIME_DELAY)

def add_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username','-u')
    parser.add_argument('--password','-p')
    parser.add_argument('--get_submissions','-gs',default=False,type=bool,help='get your submission lists of all time.')
    parser.add_argument('--build_table','-bt',default=False,type=bool,help='build contests table.')
    parser.add_argument('--refresh_table','-rt',) # TODO
    parser.add_argument('--start',default=200,type=int,help='build contests table from this number of weekly contest.')
    parser.add_argument('--end',type=int,help='build contests table to this number of weekly contest.')
    parser.add_argument('--bi_pass',defult=False,type=bool,help='whether to ignore biweekly contests when building table')
    parser.add_argument('--get_contest','-gc',help='get single weekly or biweekly contest data: \nweekly contest 200 -> input 200; biweekly contest 50 ->input b50')
    parser.add_argument('--save','-s',default=False,type=bool,help='save data to file.')
    parser.add_argument('--save_path',help='save file to the path.')
    return parser

if __name__ == '__main__':
    parser = add_args()
    args = parser.parse_args()

    login(driver, username=args.username, password=args.password)

    if args.get_submissions:
        if args.save_path is None: args.save_path = 'submission.csv'
        submissions = get_submissions(driver,args.save,args.save_path)
    
    if args.build_table:
        assert args.end is not None, 'build_table needs argument \'--end\''
        if args.save_path is None: args.save_path = 'contests_info.csv'
        get_contests(args.start,args.end,args.save_path,args.bi_pass)

    contests_df = get_contests(end=228, save=True)
    contests_df = get_contests(contest_No, save=True)
    post_info(url=url)

    driver.close()

