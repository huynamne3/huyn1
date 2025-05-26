
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time
import uuid
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__, template_folder='templates')
CORS(app)

# User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15E148 Safari/604.1",
]

# Emojis and random messages
EMOJIS = ["😂", "🤣", "😎", "💀", "🔥", "🤡", "👻", "😈", "👽", "🫠", "🥶", "😱", "🤯", "🧠", "💣", "🗿"]
RANDOM_MESSAGES = [
    "Đã 6677 rồi còn dùng nglink trẻ trâu thế hệ mới hả em",
    "Gửi làm gì nữa, ai thèm rep đâu",
    "Trẻ trâu phát hiện dùng ngl =))",
    "Còn dùng ngl là còn sống ảo",
    "Em bị bỏ rơi trên ngl phải không?"
]

# Load proxies from file (only IP:PORT format, no http://)
with open("live_proxies.txt", "r") as f:
    PROXIES_LIST = [line.strip() for line in f if line.strip()]

def get_random_message():
    msg = random.choice(RANDOM_MESSAGES)
    emojis = " ".join(random.choices(EMOJIS, k=random.randint(1, 3)))
    return f"{msg} {emojis}"

def get_random_proxy():
    proxy = random.choice(PROXIES_LIST)
    return {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }

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
        proxy = get_random_proxy()
        response = requests.post("https://ngl.link/api/submit", headers=headers, data=payload, proxies=proxy, timeout=10)
        print(f"[{index+1}] {proxy['http']} - Status: {response.status_code}")
        return {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'message': f"Đã gửi {index+1}",
            'response': response.text
        }
    except Exception as e:
        print(f"[{index+1}] Proxy error: {e}")
        return {
            'status_code': 0,
            'success': False,
            'message': f"Lỗi proxy tại {index+1}",
            'response': str(e)
        }

@app.route('/check-username')
def check_username():
    username = request.args.get('username')
    try:
        headers = { "User-Agent": random.choice(USER_AGENTS) }
        proxy = get_random_proxy()
        res = requests.get(f"https://ngl.link/{username}", headers=headers, proxies=proxy, timeout=10)
        return jsonify({'exists': res.status_code == 200 and "This page isn't available" not in res.text})
    except Exception as e:
        return jsonify({'exists': False, 'error': str(e)}), 500

@app.route('/send-attack', methods=['POST'])
def send_attack():
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')
        count = int(data.get('count', 1))

        if not username or count <= 0:
            return jsonify({'error': 'Thiếu username hoặc số lượng không hợp lệ'}), 400

        # Check once before starting attacks
        headers = { "User-Agent": random.choice(USER_AGENTS) }
        proxy = get_random_proxy()
        check_response = requests.get(f"https://ngl.link/{username}", headers=headers, proxies=proxy, timeout=10)
        if check_response.status_code != 200 or "This page isn't available" in check_response.text:
            return jsonify({'error': f'Username {username} không tồn tại trên ngl.link.'}), 400

        results = []
        MAX_THREADS = min(20, count)
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [
                executor.submit(send_single_request, username, message or get_random_message(), i)
                for i in range(count)
            ]
            for future in as_completed(futures):
                results.append(future.result())

        duration = round(time.time() - start_time, 2)
        return jsonify({'results': results, 'time_taken': f"{duration}s"})

    except Exception as e:
        print("[ERROR]", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
