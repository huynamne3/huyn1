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

# ✅ Hàm kiểm tra proxy sống qua HTTPS
def is_proxy_alive(proxy):
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        # Test bằng HTTPS để đảm bảo proxy hỗ trợ CONNECT tunnel
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
        return response.status_code == 200
    except:
        return False

# ✅ Load proxy sống vào RAM khi khởi chạy
try:
    with open("proxy.txt", "r") as f:
        all_proxies = f.read().splitlines()
        PROXIES = [p for p in all_proxies if is_proxy_alive(p)]
        print(f"✅ Đã load {len(PROXIES)} proxy sống (hỗ trợ HTTPS).")
except:
    PROXIES = []

@app.route('/')
def index():
    return render_template('index.html')

# ✅ Hàm gửi 1 request
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

    proxy = None
    if PROXIES:
        for _ in range(5):  # thử 5 proxy ngẫu nhiên
            candidate = random.choice(PROXIES)
            if is_proxy_alive(candidate):
                proxy = candidate
                break

    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    } if proxy else None

    # Thử gửi với proxy
    try:
        with requests.Session() as session:
            response = session.post("https://ngl.link/api/submit", headers=headers, data=payload, proxies=proxies, timeout=10)
        print(f"[{index+1}] ✅ Status: {response.status_code} | Proxy: {proxy}")
        return {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'message': f"Đã gửi {index+1}",
            'response': response.text
        }

    # Nếu proxy lỗi, thử lại không dùng proxy
    except Exception as e:
        print(f"[{index+1}] ❌ Lỗi với proxy {proxy}: {e}")

        try:
            response = requests.post("https://ngl.link/api/submit", headers=headers, data=payload, timeout=10)
            print(f"[{index+1}] 🔁 Fallback OK (Không dùng proxy) | Status: {response.status_code}")
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'message': f"Đã gửi {index+1} (không proxy)",
                'response': response.text
            }
        except Exception as e2:
            print(f"[{index+1}] ❌ Lỗi khi gửi fallback không proxy: {e2}")
            return {
                'status_code': 0,
                'success': False,
                'message': f"Lỗi lần 2 ở request {index+1}",
                'response': str(e2)
            }

# ✅ Gửi hàng loạt request song song
@app.route('/send-attack', methods=['POST'])
def send_attack():
    data = request.json
    username = data.get('username')
    message = data.get('message') or "Hello from bot!"
    count = int(data.get('count', 1))

    results = []

    # Tính số thread dựa trên số proxy sống
    max_threads = max(5, min(100, len(PROXIES) * 2))

    with ThreadPoolExecutor(max_workers=min(max_threads, count)) as executor:
        futures = [executor.submit(send_single_request, username, message, i) for i in range(count)]
        for future in as_completed(futures):
            results.append(future.result())

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
