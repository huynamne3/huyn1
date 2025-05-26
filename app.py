from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time
import uuid
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__, template_folder='templates')
CORS(app)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Linux; Android 10; SM-A107F) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36 Brave/91.0.4472.124"
]

EMOJIS = [
    "😂", "🤣", "😎", "💀", "🔥", "🤡", "👻", "😈", "👽", "🫠", "🥶", "😱", "🤯", "🧠", "💣", "🗿"
]

RANDOM_MESSAGES = [
    "Đã 6677 rồi còn dùng nglink trẻ trâu thế hệ mới hả em",
    "Gửi làm gì nữa, ai thèm rep đâu",
    "Trẻ trâu phát hiện dùng ngl =))",
    "Còn dùng ngl là còn sống ảo",
    "Em bị bỏ rơi trên ngl phải không?"
]

def get_random_message():
    message = random.choice(RANDOM_MESSAGES)
    emoji_count = random.randint(1, 3)
    emojis = ' '.join(random.choices(EMOJIS, k=emoji_count))
    return f"{message} {emojis}"

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
            'message': f"\u0110\u00e3 g\u1eedi {index+1}",
            'response': response.text
        }
    except Exception as e:
        print(f"[{index+1}] Error: {e}")
        return {
            'status_code': 0,
            'success': False,
            'message': f"L\u1ed7i \u1edf request {index+1}",
            'response': str(e)
        }

@app.route('/check-username')
def check_username():
    username = request.args.get('username')
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS)
        }
        res = requests.get(f"https://ngl.link/{username}", headers=headers, timeout=5)
        if res.status_code == 200 and "This page isn't available" not in res.text:
            return jsonify({'exists': True})
        else:
            return jsonify({'exists': False})
    except Exception as e:
        return jsonify({'exists': False, 'error': str(e)}), 500

@app.route('/send-attack', methods=['POST'])
def send_attack():
    try:
        data = request.json
        print("[DEBUG] D\u1eef li\u1ec7u nh\u1eadn \u0111\u01b0\u1ee3c:", data)

        username = data.get('username')
        message = data.get('message')
        count = int(data.get('count', 1))

        if not username or count <= 0:
            return jsonify({'error': 'Thi\u1ebfu username ho\u1eb7c count kh\u00f4ng h\u1ee3p l\u1ec7'}), 400

        headers = {
            "user-agent": random.choice(USER_AGENTS)
        }
        check_response = requests.get(f"https://ngl.link/{username}", headers=headers, timeout=5)
        if check_response.status_code != 200 or "This page isn't available" in check_response.text:
            return jsonify({'error': f'Username {username} kh\u00f4ng t\u1ed3n t\u1ea1i tr\u00ean ngl.link.'}), 400

        results = []
        MAX_THREADS = min(50, count)
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(send_single_request, username, message or get_random_message(), i) for i in range(count)]
            for future in as_completed(futures):
                res = future.result()
                results.append(res)

        duration = round(time.time() - start_time, 2)
        return jsonify({'results': results, 'time_taken': f"{duration}s"})

    except Exception as e:
        print("[ERROR] L\u1ed7i t\u1ea1i /send-attack:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
