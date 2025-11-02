import requests

token = "8059342403:AAE7BOZcQesYM3JLHBCcAyldhSLfcFSsj3U"
user_id = 6380709159
message = "Chào bạn Hieu! Đây là tin nhắn từ bot 😄"

requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={
    "chat_id": user_id,
    "text": message
})
