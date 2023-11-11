from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd
import urllib.request
import csv
import sys
import re

def getHTML(url):
    # Open the URL
    # Spoof the user agent

    header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
    }
    
    request = Request(url, headers=header)
    
    # Read the response as HTML
    try:
        urlopen(request).read()
        html = urlopen(request).read().decode('ascii', 'ignore')
        if len(re.findall('error-desc', html)) > 0:
            return None
        else:
            return html
    except urllib.error.HTTPError as err:
        print("{} for {}".format(err.code, url))
        return None

def getDriverHTML(url):
    # Set driver options
    options = Options()
    #options.add_argument('--headless')

    # Set Chrome driver
    driver = webdriver.Chrome()
    driver.implicitly_wait(0.3) # wait in seconds

    driver.get(url)
    
    # Accepting cookies
    driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()

    response = driver.page_source

    driver.close()

    soup = BeautifulSoup(response, 'html.parser')

    return response, soup

def concat_tags(tags):
    # List to append results 
    results = []

    # Cycle through tags two by two and concatenate them
    for i in range(0, len(tags), 2):
        concatenated = BeautifulSoup(str(tags[i]) + str(tags[i + 1]), 'html.parser')
        results.append(concatenated)

    return results

def tabulate(file, NewData):
    # This function goal is to add new data in the existing file
    try:
        # Get existing data
        existingData = pd.read_csv(rf'data/{file}.csv', sep=',', encoding='utf-8')

        # Concat both new and old data
        NewData = pd.concat([existingData, NewData], axis=0)

        NewData = NewData.drop_duplicates() # remove duplicates
    
    except:
        print('File not found.')
    
    finally:
        # Save new file
        NewData.to_csv(rf'data/{file}.csv', encoding='utf-8', index=False)
        print('File saved!')