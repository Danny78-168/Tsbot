import os
import json
import time
import random
import requests
from openai import OpenAI

# 1. 初始化 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. 娛樂城/遊戲相關的精美圖片庫網址（確保是直連網址，方便 Threads 抓取）
IMAGE_POOL = [
    "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1080&auto=format&fit=crop&q=80", # 質感風格
    "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=1080&auto=format&fit=crop&q=80", # 遊戲/娛樂感
    "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1080&auto=format&fit=crop&q=80"  # 科技/電子感
]

def generate_casino_post(account_name):
    """使用 GPT-6 Astra 生成包含指定關鍵字的吸引人貼文"""
    prompt = f"""
    請以吸引玩家、輕鬆幽默且帶有強烈互動的繁體中文風格，為 Threads 帳號「{account_name}」撰寫一篇關於線上娛樂的貼文。
    貼文內容必須自然融入以下部分或全部關鍵字：「娛樂城、優惠、首儲、電子、百家、真人、捕魚、老虎機、角子」。
    貼文長度在 100 字以內，必須附帶 1-2 個相關 hashtag，並在結尾處自然地加上宣傳語：「更多優惠找他 @osc168」。
    """
    
    response = client.chat.completions.create(
        model="gpt-6-astra",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def publish_to_threads_with_image(user_id, access_token, text, image_url):
    """兩步驟發布 Threads 圖文貼文"""
    create_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    
    create_params = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": text,
        "access_token": access_token
    }

    res = requests.post(create_url, data=create_params).json()
    creation_id = res.get("id")
    if not creation_id:
        print(f"建立圖文容器失敗: {res}")
        return False

    # 等待 Meta 伺服器下載圖片
    time.sleep(10)

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

    for acc in accounts:
        print(f"正在處理帳號：{acc.get('name')}")
        
        # 1. 透過 GPT-6 Astra 生成帶關鍵字的文案
        content = generate_casino_post(acc.get("name"))
        print(f"生成文案：\n{content}\n")
        
        # 2. 隨機挑選一張配合的圖片
        selected_image = random.choice(IMAGE_POOL)
        
        # 3. 發布圖文至 Threads
        success = publish_to_threads_with_image(acc["user_id"], acc["token"], content, selected_image)
        
        # 帳號間隔發布，避免過快被限制
        time.sleep(15)

if __name__ == "__main__":
    main()
