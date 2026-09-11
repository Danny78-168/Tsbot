import os
import json
import time
import requests
from openai import OpenAI

# 1. 初始化 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def publish_to_threads(user_id, access_token, text):
    """純文字發布 Threads 貼文"""
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

    # 短暫暫停確保容器就緒
    time.sleep(3)

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
    accounts_data = os.getenv("THREADS_ACCOUNTS_JSON")
    if not accounts_data:
        print("未設定 THREADS_ACCOUNTS_JSON")
        return

    accounts = json.loads(accounts_data)
    
    # 讀取手動自訂文案
    custom_text = os.getenv("CUSTOM_POST_TEXT")

    for acc in accounts:
        print(f"正在處理帳號：{acc.get('name')}")
        
        # 判斷要用手動自訂文案還是 GPT-6 Astra 生成
        if custom_text and custom_text.strip() != "":
            content = custom_text.strip()
            print(f"成功讀取到手動自訂文案：\n{content}\n")
        else:
            print("未偵測到自訂文案，改由 GPT-6 Astra 自動生成...")
            prompt = f"請以輕鬆幽默的繁體中文風格，為 Threads 帳號「{acc.get('name')}」撰寫一篇 100 字以內的日常貼文，附帶 1-2 個 hashtag。"
            response = client.chat.completions.create(
                model="gpt-6-astra",  # 使用最新的 GPT-6 Astra 模型
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
            )
            content = response.choices[0].message.content.strip()
            print(f"GPT-6 Astra 生成文案：\n{content}\n")

        # 發布純文字至 Threads
        success = publish_to_threads(acc["user_id"], acc["token"], content)
        
        # 帳號間隔
        time.sleep(5)

if __name__ == "__main__":
    main()
