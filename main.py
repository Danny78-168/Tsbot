import os
import json
import time
import requests
from openai import OpenAI

# 1. 初始化 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_thread_post(account_name):
    """呼叫 OpenAI 自動生成文案與圖片關鍵字"""
    prompt = f"""請以輕鬆幽默、吸引互動的繁體中文風格，為 Threads 帳號「{account_name}」撰寫一篇 100 字以內的日常閒聊或乾貨貼文，附帶 1-2 個 hashtag。
另外，請在回覆的最下方用這一行格式告訴我一個對應的英文圖片關鍵字（例如: coffee, technology, nature, food, cat, office）：
KEYWORD: [你的英文關鍵字]"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    full_text = response.choices[0].message.content.strip()
    
    # 解析文案與關鍵字
    if "KEYWORD:" in full_text:
        parts = full_text.split("KEYWORD:")
        post_content = parts[0].strip()
        keyword = parts[1].strip().replace("[", "").replace("]", "").strip()
    else:
        post_content = full_text
        keyword = "nature" # 預設關鍵字
        
    return post_content, keyword

def get_relevant_image_url(keyword):
    """根據 AI 提供的關鍵字取得相關的高畫質圖片網址"""
    # 使用 Unsplash Source 根據關鍵字動態抓取圖片
    image_url = f"https://source.unsplash.com/featured/1080x1080/?{keyword}"
    return image_url

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

    # 等待 Meta 伺服器下載圖片
    time.sleep(6)

    # 發布容器內容
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
        
        # 1. 生成文案與圖片關鍵字
        content, keyword = generate_thread_post(acc.get("name"))
        print(f"生成文案：\n{content}\n")
        print(f"AI 決定的圖片主題：{keyword}")
        
        # 2. 取得對應的關聯圖片網址
        img_url = get_relevant_image_url(keyword)
        print(f"圖片網址：{img_url}")
        
        # 3. 發布至 Threads
        success = publish_to_threads(acc["user_id"], acc["token"], content, img_url)
        
        # 帳號間間隔發布
        time.sleep(10)

if __name__ == "__main__":
    main()
