import re
import requests
import datetime
from bs4 import BeautifulSoup
import time

def get_parsed_page(url, delay=0.5):
    # This fixes a blocked by cloudflare error i've encountered
    headers = {
        "referer": "https://www.hltv.org/stats",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    cookies = {
        "hltvTimeZone": HLTV_COOKIE_TIMEZONE
    }

    time.sleep(delay)

    return BeautifulSoup(requests.get(url, headers=headers, cookies=cookies).text, "lxml")