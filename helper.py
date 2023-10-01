from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
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
    options.add_argument('--headless')

    # Set Chrome driver
    driver = webdriver.Chrome()
    driver.implicitly_wait(1) # wait 1s

    url = 'https://www.hltv.org/matches/{}'.format(url)

    driver.get(url)
    
    # Accepting cookies
    driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()

    response = driver.page_source

    driver.close()

    return response
