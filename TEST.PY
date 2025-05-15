import requests, json, os
import environ
from dotenv import load_dotenv
env = environ.Env()
environ.Env.read_env()

load_dotenv()

SUPABASE_URL = env("SUPABASE_URL")
SUPABASE_API_KEY = env("SUPABASE_API_KEY")
TABLE_NAME = env("TABLE_NAME")

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
# TABLE_NAME = os.getenv("TABLE_NAME")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# Giả sử bạn lưu JSON trên vào file "data.json"
with open("data/crawl_data/vocab/vocabulary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Đổi key về đúng cột tên (lower case không dấu tiếng Việt)
formatted_data = [
    {
        "topic": item.get("Topic", ""),
        "english": item.get("English", ""),
        "ipa": item.get("IPA", ""),
        "type": item.get("Type", ""),
        "vietnamese": item.get("Vietnamese", "")
    }
    for item in data
]

# Gửi lên Supabase (chia nhỏ batch nếu lớn)
response = requests.post(
    f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}",
    headers=headers,
    data=json.dumps(formatted_data)
)

print(response.status_code, response.text)
