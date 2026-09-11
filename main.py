import os

# 這樣就能抓到 GitHub Secrets 裡的密碼，而不用把密碼寫死在程式碼裡
openai_key = os.environ.get("OPENAI_API_KEY")
threads_token = os.environ.get("THREADS_ACCESS_TOKEN")

# 測試是否有抓到 (注意：實際發布時請把 print 密碼的行數刪除，以免密碼外洩在日誌中)
print("已成功載入 API Keys (長度):", len(str(openai_key)))
