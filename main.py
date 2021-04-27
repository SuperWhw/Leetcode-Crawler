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

dir_path = os.path.dirname(os.path.abspath(__file__))
driver_path = os.path.join(dir_path, 'chromedriver.exe')
chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--incognito')
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(driver_path,options=chrome_options)
driver.implicitly_wait(TIME_DELAY)

def parse_command_line():
    parser = argparse.ArgumentParser()

    # user info
    parser.add_argument('--username','-u')
    parser.add_argument('--password','-p')

    # get submissions
    parser.add_argument('--get_submissions',
                        '-gs',
                        action='store_true',
                        default=False,
                        help='Get your submission lists of all time.')
    parser.add_argument('--save_submissions_path',
                        '-ssp',
                        default='submission.csv',
                        type=str,
                        help='Path for saving submissions table.')
    
    # get contests table
    parser.add_argument('--build_table',
                        '-bt',
                        action='store_true',
                        default=False,
                        help='Build contests table.')
    parser.add_argument('--rewrite',
                        action='store_true',
                        default=False,
                        help='If contest data already exists in file, whether to rewrite new data. Default is false.')
    parser.add_argument('--start',
                        default=200,
                        type=int,
                        help='Build contests table from this number of weekly contest.')
    parser.add_argument('--end',
                        type=int,
                        help='Build contests table to this number of weekly contest.')
    parser.add_argument('--save_path',
                        default='data/contests_info.csv',
                        type=str,
                        help='Save file.')
    
    # Post stat comment for a contest 
    parser.add_argument('--post_url',
                    default=None,
                    type=str,
                    help='Where to post the contest info.')
    
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_command_line()

    login(driver, username=args.username, password=args.password)

    if args.get_submissions:
        submissions = get_submissions(driver,args)
    
    if args.build_table:
        assert args.end is not None, 'build_table needs argument \'--end\''
        get_contests(driver, args)

    if args.post_url is not None:
        post_info(driver, args)

    driver.close()

