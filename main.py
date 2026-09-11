import os
import json
import time
import requests
from openai import OpenAI

# 1. 初始化 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_thread_post(account_name):
    """呼叫 OpenAI 自動生成文案"""
    prompt = f"請以輕鬆幽默、吸引互動的繁體中文風格，為 Threads 帳號「{account_name}」撰寫一篇 100 字以內的日常閒聊或乾貨貼文，附帶 1-2 個 hashtag。"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()

def publish_to_threads(user_id, access_token, text):
    """兩步驟發布 Threads 貼文"""
    # 步驟 A: 建立貼文容器 (Media Container)
    create_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    create_params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": access_token
    }
    res = requests.post(create_url, data=create_params).json()
    creation_id = res.get("id")
    if not creation_id:
        print(f"建立容器失敗: {res}")
        return False

    # 確保伺服器處理完畢，稍等 5 秒
    time.sleep(5)

    # 步驟 B: 發布容器內容
    publish_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    publish_params = {
        "creation_id": creation_id,
        "access_token": access_token
    }
    pub_res = requests.post(publish_url, data=publish_params).json()
    if "id" in pub_res:
        print(f"發布成功！貼文 ID: {pub_res['id']}")
        return True
    else:
        print(f"發布失敗: {pub_res}")
        return False

def main():
    # 讀取多帳號資訊
    accounts_data = os.getenv("THREADS_ACCOUNTS_JSON")
    if not accounts_data:
        print("未設定 THREADS_ACCOUNTS_JSON")
        return

    accounts = json.loads(accounts_data)

    for acc in accounts:
        print(f"正在處理帳號：{acc.get('name')}")
        content = generate_thread_post(acc.get("name"))
        print(f"生成文案：\n{content}\n")
        
        success = publish_to_threads(acc["user_id"], acc["token"], content)
        # 帳號間間隔發布，避免短時間內連鎖請求
        time.sleep(10)

if __name__ == "__main__":
    main()
