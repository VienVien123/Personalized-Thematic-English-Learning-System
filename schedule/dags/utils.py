import os
# import re
# import pytz
# import random
# import requests
import psycopg2
# import feedparser
from time import sleep
from psycopg2 import extras
# from datetime import datetime
from logger import get_logger
# from bs4 import BeautifulSoup
from dotenv import load_dotenv
# from concurrent.futures import as_completed
# from concurrent.futures import ThreadPoolExecutor

load_dotenv()
OPTIONS=os.getenv("OPTIONS")
MAX_WORKERS=os.getenv("MAX_WORKERS", 5)
API_SENTIMENT= os.getenv("API_SENTIMENT")
logger = get_logger(logs_dir='/var/log/vien/', log_filename='update_rotoro_db.log')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
api_sentiment = os.getenv("API_SENTIMENT")

POSTGRES_DB_NEWS = os.getenv("POSTGRES_DB_NEWS")
POSTGRES_USER_NEWS = os.getenv("POSTGRES_USER_NEWS")
POSTGRES_PASSWORD_NEWS = os.getenv("POSTGRES_PASSWORD_NEWS")
POSTGRES_HOST_NEWS = os.getenv("PG_HOST_NEWS")
POSTGRES_PORT_NEWS = os.getenv("PG_PORT_NEWS")


class Postgres:
    def __init__(self):
        self.host = POSTGRES_HOST_NEWS
        self.user = POSTGRES_USER_NEWS
        self.password = POSTGRES_PASSWORD_NEWS
        self.db = POSTGRES_DB_NEWS
        self.port = POSTGRES_PORT_NEWS
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.db
            )
            self.cursor = self.conn.cursor(cursor_factory=extras.DictCursor)
        except Exception as e:
            print(f"❌ Lỗi khi kết nối PostgreSQL: {e}")
            raise

    def execute_write(self, query, data=None):
        try:
            self.cursor.execute(query, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Lỗi khi ghi dữ liệu: {e}")
            raise

    def execute_read(self, query, data=None):
        try:
            self.cursor.execute(query, data)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Lỗi khi đọc dữ liệu: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def is_connected(self):
        try:
            self.cursor.execute("SELECT 1;")
            return True
        except Exception:
            return False

    def run_sql_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                sql = f.read()
            self.cursor.execute(sql)
            self.conn.commit()
            print(f"✅ Thực thi file SQL thành công: {file_path}")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Lỗi khi chạy file SQL: {e}")
            raise

    def get_columns(self, table_name):
        self.cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        return [row[0] for row in self.cursor.fetchall()]

    def upsert(self, table_name: str, data: tuple, ids: list = [], updates: list = None):
        conflict_target = 'id'
        update_cols = self.get_columns(table_name)
        update_cols.remove(conflict_target)

        check_ids = [str(data[update_cols.index(id)]).replace("'", "''") for id in ids]
        updates_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_cols]) if updates is None else updates

        try:
            where_clause = ' AND '.join([f"{col} = '{val}'" for col, val in zip(ids, check_ids)])
            sql_exists = f"SELECT {conflict_target} FROM {table_name} WHERE {where_clause}"
            self.cursor.execute(sql_exists)
            result = self.cursor.fetchone()

            attrs = tuple(update_cols)
            if result:
                _id = result[0]
                data = (_id,) + data
                attrs = (conflict_target,) + attrs

            sql_insert = f"""
                INSERT INTO {table_name} ({','.join(attrs)})
                VALUES ({','.join(['%s']*len(attrs))})
                ON CONFLICT ({conflict_target})
                DO UPDATE SET {updates_clause}
                RETURNING id;
            """

            self.cursor.execute(sql_insert, data)
            returned_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return returned_id
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Lỗi khi upsert vào bảng `{table_name}`: {e}")
            return None
        
    def test_connection(self):
        try:
            self.cursor.execute("SELECT 1;")
            return True
        except Exception:
            return False
        
# def sentiment_analysis(text):
#     if text == "POSITIVE":
#         return 1
#     elif text == "NEUTRAL":
#         return 2
#     elif text == "NEGATIVE":
#         return 3
#     else:
#         return 4
    
# def insert_news_with_upsert(news_list):
#     pg = Postgres()
#     cols = pg.get_columns("news_articles") 
#     cols.remove("id")

#     for news in news_list:
#         try:
#             data = tuple(news.get(col) for col in cols)
#             pg.upsert(
#                 table_name="news_articles",
#                 data=data,
#                 ids=["link"]
#             )
#         except Exception as e:
#             logger.error(f"❌ Lỗi khi upsert bài viết {news.get('title')} vào PostgreSQL: {e}")
#     pg.close()

# def get_content(new):
#     try:
#         response = requests.get(new['link'], headers=headers)
#         sleep(random.randint(1, 3))
#         soup = BeautifulSoup(response.content, 'html.parser')
#         paragraphs = soup.find_all('p')
#         content = ""
#         for p in paragraphs:
#             content += p.get_text() + "\n"
#         cleaned_text = re.sub(r'\s+', ' ', content)  
#         cleaned_text = cleaned_text.strip() 
#         new['content'] = cleaned_text
#         logger.info(f"🟢 Đã lấy nội dung từ link: {new['link']}")
#         return new
#     except Exception as e:
#         logger.error(f"🔴 Lỗi khi lấy nội dung từ link: {new['link']}: {e}")
#         return None  

# def parse_rss_entries(rss_url):
#     feeds = [{key: feedparser.parse(value)} for key, value in rss_url.items()]
#     sleep(1)
#     news = []
#     time_format = '%a, %d %b %Y %H:%M:%S %z'
#     for feed in feeds:
#         for key, parsed_feed in feed.items():
#             for entry in parsed_feed.entries:
#                 if entry.title and entry.link and entry.published and entry.summary:
#                     soup = BeautifulSoup(entry.summary, 'html.parser')
#                     summary = soup.get_text(strip=True)
#                     dt = datetime.strptime(entry.published, time_format)
#                     dt = dt.replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh")) 
#                     temp = {
#                         'title': entry.title,
#                         'link': entry.link,
#                         'published': dt,
#                         'summary': summary,
#                         'topic': key
#                     }
#                     news.append(temp)
#     return news

# def thread_senti(news):
#     with ThreadPoolExecutor(max_workers=int(MAX_WORKERS)) as executor:
#         future_to_news = {executor.submit(get_content, new): new for new in news}
#         enriched_news = []

#         for future in as_completed(future_to_news):
#             try:
#                 result = future.result()
#                 if result:
#                     try:
#                         payload = {
#                             "text": f"{result['title']} - {result['summary']}",
#                             "entity": result['topic']
#                         }
#                         response = requests.post(api_sentiment, json=payload, timeout=10)
#                         result['sentiment'] = response.json().get('sentiment', None)
#                         if result['sentiment'] is not None:
#                             result['sentiment_score'] = sentiment_analysis(result['sentiment'])
#                     except Exception as e:
#                         logger.error(f"🔴 Lỗi khi gọi API sentiment: {e}")
#                         result['sentiment'] = None
                    
#                     enriched_news.append(result)
#                     logger.info(f"✅ Đã xử lý bài viết: {result['title']} - topic: {result['topic']}")
    
#             except Exception as e:
#                 logger.error(f"❌ Lỗi xử lý bài viết song song: {e}")
#                 continue
#     return enriched_news

# def get_rss(rss_url):
#     logger.info("🟢 Bắt đầu lấy dữ liệu từ RSS")
#     news = parse_rss_entries(rss_url)
#     logger.info(f"🟢 Đã lấy {len(news)} bài viết từ RSS")  
#     if not news:
#         logger.info("🔴 Không có bài viết nào mới từ RSS")
#         return []
#     logger.info(f"🟢 Hoàn thành lấy dư liệu cơ bản tiến hành lấy content...")
#     try:
#         logger.info(f"🟢 Đang lấy dữ liệu content và gửi sentiment")
#         enriched_news = thread_senti(news)
#         insert_news_with_upsert(enriched_news)
#         logger.info(f"🟢 Đã lưu {len(enriched_news)} bài viết vào PostgreSQL thành công")        
#         return enriched_news
#     except Exception as e:
#         logger.error(f"🔴 Lỗi khi xử lý dữ liệu content và sentiment: {e}")
#         raise


