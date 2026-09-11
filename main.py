import os
import requests
from openai import OpenAI

# 1. 取得環境變數
openai_key = os.environ.get("OPENAI_API_KEY")
threads_token = os.environ.get("THREADS_ACCESS_TOKEN")
threads_user_id = "me" # 依據 Meta API 規範，通常可以用 me 代表授權用戶

# 2. 讓 OpenAI 生成文案
client = OpenAI(api_key=openai_key)
response = client.chat.completions.create(
    model="gpt-4o", # 或 gpt-3.5-turbo
    messages=[
        {"role": "system", "content": "你是一個專業的社群小編，請幫我寫一篇適合發在 Threads 上的短文，風格幽默輕鬆。"},
        {"role": "user", "content": "請給我今天的貼文！"}
    ]
)
post_content = response.choices[0].message.content

# 3. 發布到 Threads (分為兩個步驟：建立容器 -> 發布容器)
# 步驟 A: 建立 Threads 媒體容器 (文字內容)
create_url = f"https://graph.threads.net/v19.0/{threads_user_id}/threads"
payload = {
    "media_type": "TEXT",
    "text": post_content,
    "access_token": threads_token
}
create_res = requests.post(create_url, data=payload).json()

if 'id' in create_res:
    creation_id = create_res['id']
    
    # 步驟 B: 執行發布
    publish_url = f"https://graph.threads.net/v19.0/{threads_user_id}/threads_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": threads_token
    }
    publish_res = requests.post(publish_url, data=publish_payload).json()
    print("發布成功！", publish_res)
else:
    print("建立貼文失敗：", create_res)
