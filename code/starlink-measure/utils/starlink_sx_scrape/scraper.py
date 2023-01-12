#!/usr/bin/env python3

import os
from time import sleep
from time import time
from datetime import datetime
import re
import shutil
import argparse

from config import local_stores

import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LATENCY = 'LATENCY'
AZIMUTH = 'Az'
ELEVATION = 'El'
INTERVAL = 1

def curr_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def main(args):
    chrome_options = Options()
    #chrome_options.add_argument("--disable-extensions")
    #chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--no-sandbox") # linux only

    chrome_options.add_argument("--headless")
    print("Running headless mode")

    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.headless = True # also works

    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://starlink.sx')
    driver.implicitly_wait(5)

    for key, val in local_stores.items():
        driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, val)

    driver.refresh()
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "satellites-table"))
    )

    file_timestamp = curr_timestamp()
    os.makedirs(args.folder, exist_ok=True)
    dest_path = os.path.join(args.folder, f"{args.name}_{file_timestamp}.csv")
    print("Saving to", dest_path)

    while True:
        time_start = time()
        content = driver.page_source

        soup = BeautifulSoup(content, 'html.parser')
        num_sats_str = str(soup.find('div', dict(id='satellites')))
        num_sats = re.search('(\d+)', num_sats_str).group()
        
        sat_table = soup.find("tbody", dict(id='satellites-table')).parent
        df_table = pd.read_html(str(sat_table))[0]
        df_table[LATENCY] = df_table[LATENCY].str.extract('(\d+\.\d+)', expand=False)
        df_table[AZIMUTH] = df_table[AZIMUTH].str.extract('(\d+\.?\d*)', expand=False)
        df_table[ELEVATION] = df_table[ELEVATION].str.extract('(\d+\.?\d*)', expand=False)
        df_table['timestamp'] = driver.execute_script("return window.time_marker;")
        df_table['connectable_sats'] = num_sats

        df_table.to_csv(dest_path, mode='a', index=False, header=not os.path.exists(dest_path))

        time_end = time()
        elapsed = time_end - time_start
        if INTERVAL > elapsed:
            sleep(INTERVAL - elapsed)

    driver.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape starlink.sx to get satellite data.")
    parser.add_argument('-f', '--folder', default='starlink_satellite_data', help='Destination folder for CSV files.')
    parser.add_argument('-n', '--name', default='satellites', help='Prefix filename of CSV file.')
    args = parser.parse_args()
    main(args)
