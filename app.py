from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time
import uuid
import random

app = Flask(__name__, template_folder='templates')
CORS(app)

RANDOM_MESSAGES = [
    "Bạn thật tuyệt vời!", 
    "Ai đó đang nghĩ về bạn 😘", 
    "Thử đoán xem tôi là ai nào?", 
    "Một người bí ẩn gửi lời chào 💌", 
    "Chúc bạn một ngày vui vẻ!", 
    "Bạn có đang nhớ ai không? 🤔",
    "Tin nhắn ngẫu nhiên từ vũ trụ!",
    "Đừng lo, mọi chuyện sẽ ổn!",
    "Người gửi xin được giấu tên 😉",
    "Bạn đang được theo dõi 🙈"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-attack', methods=['POST'])
def send_attack():
    data = request.json
    print("[REQUEST]", data)
    username = data.get('username')
    message = data.get('message')
    if not message or message.strip() == "":
        message = random.choice(RANDOM_MESSAGES)
    count = int(data.get('count', 1))

    results = []
    for i in range(count):
        headers = {
            "Host": "ngl.link",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://ngl.link",
            "referer": f"https://ngl.link/{username}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        payload = {
            "username": username,
            "question": message,
            "deviceId": str(uuid.uuid4()),
            "gameSlug": "",
            "referrer": ""
        }

        response = requests.post("https://ngl.link/api/submit", headers=headers, data=payload)

        print(f"[{i+1}] Status Code: {response.status_code}")
        print(f"[{i+1}] Response Text: {response.text}")

        results.append({
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'message': f"Đã gửi {i+1}/{count}",
            'response': response.text
        })

        time.sleep(0.5)

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
