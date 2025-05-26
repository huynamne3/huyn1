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
USER_AGENTS = [ ... ]  # (Giữ nguyên như bạn đã có)

# Đọc danh sách proxy vào RAM (khi khởi chạy)
try:
    with open("proxy.txt", "r") as f:
        PROXIES = f.read().splitlines()
except:
    PROXIES = []

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

    proxy = random.choice(PROXIES) if PROXIES else None
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    } if proxy else None

    try:
        with requests.Session() as session:
            response = session.post("https://ngl.link/api/submit", headers=headers, data=payload, proxies=proxies, timeout=10)
        print(f"[{index+1}] Status Code: {response.status_code} | Proxy: {proxy}")
        return {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'message': f"Đã gửi {index+1}",
            'response': response.text
        }
    except Exception as e:
        print(f"[{index+1}] Error with proxy {proxy}: {e}")
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

    MAX_THREADS = min(30, count)

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(send_single_request, username, message, i) for i in range(count)]
        for future in as_completed(futures):
            results.append(future.result())

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
