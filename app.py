from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time
import uuid
import random

app = Flask(__name__, template_folder='templates')
CORS(app)

# Danh sách User-Agent đa dạng
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-A107F) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 Version/13.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-attack', methods=['POST'])
def send_attack():
    data = request.json
    print("[REQUEST]", data)
    username = data.get('username')
    message = data.get('message') or "Hello from bot!"
    count = int(data.get('count', 1))

    results = []
    for i in range(count):
        # Chọn random user-agent mỗi lần gửi
        user_agent = random.choice(USER_AGENTS)
        headers = {
            "Host": "ngl.link",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://ngl.link",
            "referer": f"https://ngl.link/{username}",
            "user-agent": user_agent
        }

        payload = {
            "username": username,
            "question": message,
            "deviceId": str(uuid.uuid4()),
            "gameSlug": "",
            "referrer": ""
        }

        try:
            response = requests.post("https://ngl.link/api/submit", headers=headers, data=payload)
            print(f"[{i+1}] Status Code: {response.status_code}")
            print(f"[{i+1}] Response Text: {response.text}")
        except Exception as e:
            print(f"[{i+1}] Lỗi gửi: {e}")
            response = type('obj', (object,), {'status_code': 500, 'text': str(e)})

        results.append({
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'message': f"Đã gửi {i+1}/{count}",
            'response': response.text
        })

        # Delay nhỏ để tránh bị chặn, có thể giảm xuống 0.3 hoặc thấp hơn
        time.sleep(0.5)

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
