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
        model="gpt-4o",  # 已升級為高階模型以獲得更好的文案品質
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()

def generate_image_for_post(text_content):
    """利用 DALL-E 3 根據文案內容自動生成一張相關圖片的公開網址"""
    try:
        image_prompt = f"為以下社群貼文創作一張適合的插畫或照片，風格現代、明亮、吸引人：{text_content}"
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"生成圖片失敗: {e}")
        return None

def publish_to_threads(user_id, access_token, text, image_url=None):
    """兩步驟發布 Threads 圖文貼文"""
    # 步驟 A: 建立貼文容器 (Media Container)
    create_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    
    if image_url:
        # 如果有圖片，使用 IMAGE 類型
        create_params = {
            "media_type": "IMAGE",
            "image_url": image_url,
            "text": text,
            "access_token": access_token
        }
    else:
        # 如果沒有圖片，維持純文字
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

    # 確保 Meta 伺服器下載並處理完圖片，稍等 10 秒
    time.sleep(10)

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
        
        # 1. 生成文案
        content = generate_thread_post(acc.get("name"))
        print(f"生成文案：\n{content}\n")
        
        # 2. 根據文案生成配圖
        print("正在為貼文繪製圖片...")
        img_url = generate_image_for_post(content)
        
        # 3. 發布至 Threads
        success = publish_to_threads(acc["user_id"], acc["token"], content, img_url)
        
        # 帳號間間隔發布
        time.sleep(15)

if __name__ == "__main__":
    main()
