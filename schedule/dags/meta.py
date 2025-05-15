# import os
import re
# import json
# import random
# import logging
import requests
import pendulum
# import feedparser
from time import sleep
from airflow import DAG
from logger import get_logger
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient
from airflow.decorators import task
from datetime import datetime, timedelta
from utils import   Postgres
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

load_dotenv()

logger = get_logger(logs_dir='/var/log/vien/', log_filename='update_rotoro_db.log')

default_args = {
    'owner': 'social',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'daily_keyword_to_kafka',
    default_args=default_args,
    description='Chạy cách 8 tiếng một lần',
    schedule_interval='0 */8 * * *',
    start_date=datetime(2025, 1, 3, tzinfo=pendulum.timezone("Asia/Ho_Chi_Minh")),
    catchup=False,
) as dag:
    
    # @task
    # def get_data():
    #     try:
    #         logger.info("🟢 Bắt đầu lấy từ khóa từ RSS")

    #         pg = Postgres()
    #         if pg.test_connection():
    #             logger.info("🟢 Kết nối thành công đến cơ sở dữ liệu PostgreSQL")
    #         else:
    #             logger.error("🔴 Không thể kết nối đến cơ sở dữ liệu PostgreSQL")
    #     except Exception as e:
    #         logger.error(f"🔴 Lỗi khi lấy dữ liệu từ RSS: {e}")
    #         raise

    @task
    def get_data():
        try:
            logger.info("🟢 Bắt đầu lấy từ vựng từ trang tuhocielts.vn")

            url = 'https://www.tuhocielts.vn/tai-hon-3000-tu-tieng-anh-thong-dung-theo-chu-de-pdf-free/'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', class_='entry-content')

            text_vocab = []
            current_title = ""
            for elem in content_div.find_all(['h3', 'p']):
                if elem.name == 'h3':
                    raw_title = elem.get_text(strip=True)
                    match_title = re.search(r"(chủ đề.*)", raw_title, re.IGNORECASE)
                    current_title = match_title.group(1).strip() if match_title else raw_title
                elif elem.name == 'p':
                    lines = elem.get_text().split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line or ':' not in line:
                            continue

                        match = re.match(r"""^([\w\-\s]+)(?:\s*/([^/]+)/)?(?:\s*\(([^)]+)\))?\s*:\s*(.+)$""", line)
                        if match:
                            word = match.group(1).strip()
                            ipa = f"/{match.group(2).strip()}/" if match.group(2) else ""
                            word_type = match.group(3).strip() if match.group(3) else ""
                            meaning = match.group(4).strip()

                            text_vocab.append((current_title, word, ipa, word_type, meaning, True))

            logger.info(f"📘 Đã lấy được {len(text_vocab)} từ vựng.")

            # Clean topic name
            def clean_topic_name(x):
                x = re.sub(r'^[\s\d\.,]+', '', x)
                x = re.sub(r'[\.,]+$', '', x)
                return x.strip()

            text_vocab = [(clean_topic_name(t), e, i, tp, v, s) for t, e, i, tp, v, s in text_vocab]

            pg = Postgres()
            if not pg.test_connection():
                logger.error("🔴 Không thể kết nối đến PostgreSQL")
                return

            insert_query = """
            INSERT INTO "learning_topicvocab" (topic, english, ipa, type, vietnamese, synced)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """

            for row in text_vocab:
                try:
                    pg.execute_write(insert_query, row)
                except Exception as err:
                    logger.warning(f"⚠️ Bỏ qua 1 từ lỗi: {row[1]} - {err}")
                    continue
            pg.close()
            logger.info("✅ Đã ghi dữ liệu vào bảng TopicVocab xong!")
            logger.info(" Đã hoàn thành việc lấy từ vựng từ tuhocielts.vn bao gồm {} từ vựng.".format(len(text_vocab))) 
        except Exception as e:
            logger.error(f"❌ Lỗi trong task get_data: {e}")
            raise

    get_data()


            # rss_url = {
            #     "giaitri":"https://vnexpress.net/rss/giai-tri.rss",
            #     "kinhdoanh":"https://vnexpress.net/rss/kinh-doanh.rss",
            #     "tintucmoi":"https://vnexpress.net/rss/tin-moi-nhat.rss"
            #     }  
            # news = get_rss(rss_url)
            # return news