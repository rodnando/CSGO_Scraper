from multiprocessing.dummy import Pool as ThreadPool
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