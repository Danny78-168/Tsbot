import os
import json
import time
import requests
from openai import OpenAI

# 1. 初始化 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_relevant_image_url(keyword):
    """根據關鍵字取得相關的高畫質圖片網址"""
    return f"https://source.unsplash.com/featured/1080x1080/?{keyword}"

def publish_to_threads(user_id, access_token, text, image_url=None):
    """兩步驟發布 Threads 圖文貼文"""
    create_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    
    if image_url:
        create_params = {
            "media_type": "IMAGE",
            "image_url": image_url,
            "text": text,
            "access_token": access_token
        }
    else:
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

    time.sleep(6)

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
    
    # 檢查是否有手動輸入的自訂文案
    custom_text = os.getenv("CUSTOM_POST_TEXT")

    for acc in accounts:
        print(f"正在處理帳號：{acc.get('name')}")
        
        if custom_text and custom_text.strip():
            # 使用你手動輸入的內容
            content = custom_text.strip()
            keyword = "lifestyle" # 預設配圖關鍵字
            print(f"使用手動自訂文案：\n{content}\n")
        else:
            # 如果沒有手動輸入，就交給 OpenAI 自動生成
            print("未偵測到自訂文案，改由 AI 自動生成...")
            prompt = f"請以輕鬆幽默的繁體中文風格，為 Threads 帳號「{acc.get('name')}」撰寫一篇 100 字以內的日常貼文，附帶 1-2 個 hashtag。並在結尾加上 KEYWORD: [英文關鍵字]"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
            )
            full_text = response.choices[0].message.content.strip()
            if "KEYWORD:" in full_text:
                parts = full_text.split("KEYWORD:")
                content = parts[0].strip()
                keyword = parts[1].strip().replace("[", "").replace("]", "").strip()
            else:
                content = full_text
                keyword = "nature"
            print(f"AI 生成文案：\n{content}\n")

        # 取得圖片並發布
        img_url = get_relevant_image_url(keyword)
        success = publish_to_threads(acc["user_id"], acc["token"], content, img_url)
        
        time.sleep(10)

if __name__ == "__main__":
    main()
