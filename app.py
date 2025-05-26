from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time
import uuid
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__, template_folder='templates')
CORS(app)

# Danh sách User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15E148 Safari/604.1"
]

# Danh sách emoji và message
EMOJIS = ["😂", "🤣", "😎", "💀", "🔥", "🤡", "👻", "😈", "👽", "🫠", "🥶", "😱"]
MESSAGES = [
    "Đã 6677 rồi còn dùng nglink trẻ trâu thế hệ mới hả em",
    "Còn sống ảo tới bao giờ?",
    "Dùng ngl nhìn là biết FA",
    "Rep tin nhắn đi má!",
    "Bỏ cái app trẻ trâu này đi!"
]

# Đọc proxy từ file
def load_proxies():
    try:
        with open("live_proxies.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print("[ERROR] Load proxy:", e)
        return []

PROXIES = load_proxies()

def get_random_message():
    msg = random.choice(MESSAGES)
    emoji = " ".join(random.choices(EMOJIS, k=random.randint(1, 3)))
    return f"{msg} {emoji}"

def send_single_request(username, message, index):
    proxy = random.choice(PROXIES)
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }

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
        response = requests.post("https://ngl.link/api/submit", headers=headers, data=payload, proxies=proxies, timeout=10)
        print(f"[{index+1}] {proxy} => {response.status_code}")
        return {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'message': f"Đã gửi {index+1}",
            'proxy': proxy
        }
    except Exception as e:
        return {
            'status_code': 0,
            'success': False,
            'message': f"Lỗi gửi {index+1}",
            'proxy': proxy
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-attack', methods=['POST'])
def send_attack():
    data = request.json
    username = data.get('username')
    message = data.get('message')
    count = int(data.get('count', 1))

    if not username or count <= 0:
        return jsonify({'error': 'Thiếu username hoặc số lần spam không hợp lệ'}), 400

    results = []
    MAX_THREADS = min(100, count)
    start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [
            executor.submit(send_single_request, username, message or get_random_message(), i)
            for i in range(count)
        ]
        for future in as_completed(futures):
            results.append(future.result())

    duration = round(time.time() - start, 2)
    return jsonify({'results': results, 'time_taken': f"{duration}s"})

if __name__ == '__main__':
    app.run(debug=True)
