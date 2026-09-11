import os
import json
import time
import requests
import openai

# 設定 OpenAI API Key (舊版寫法)
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_casino_text_post(account_name):
    """使用舊版 OpenAI 介面生成純文字娛樂城貼文"""
    prompt = f"""
    請以吸引線上娛樂玩家、輕鬆幽默且帶有強烈互動的繁體中文風格，為 Threads 帳號「{account_name}」撰寫一篇日常推廣貼文。
    內容必須自然融入以下部分或全部關鍵字：「娛樂城、優惠、首儲、電子、百家、真人、捕魚、老虎機、角子」。
    貼文長度在 100 字以內，必須附帶 1-2 個相關 hashtag，並在結尾處明確加上宣傳導流語：「優惠找他 @osc168」。
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content'].strip()

def publish_text_to_threads(user_id, access_token, text):
    """發布純文字 Threads 貼文"""
    create_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    
    create_params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": access_token
    }

    res = requests.post(create_url, data=create_params).json()
    creation_id = res.get("id")
    if not creation_id:
        print(f"建立純文字容器失敗: {res}")
        return False

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

    for acc in accounts:
        print(f"正在處理帳號：{acc.get('name')}")
        
        content = generate_casino_text_post(acc.get("name"))
        print(f"生成的純文字文案：\n{content}\n")
        
        success = publish_text_to_threads(acc["user_id"], acc["token"], content)
        
        time.sleep(10)

if __name__ == "__main__":
    main()
