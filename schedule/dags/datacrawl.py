import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.tuhocielts.vn/tai-hon-3000-tu-tieng-anh-thong-dung-theo-chu-de-pdf-free/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}


response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')