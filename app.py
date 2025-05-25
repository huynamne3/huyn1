from flask import Flask, request, jsonify, render_template
import threading
import random
import requests
import time

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

def load_proxies():
    global proxies
    with open("proxy.txt", "r") as f:
        proxies = [line.strip() for line in f if line.strip()]

load_proxies()

def get_proxy():
    proxy = random.choice(proxies)
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

def send_message(username, message, count, results, thread_id):
    sent = 0
    for _ in range(count):
        try:
            response = requests.post(
                'https://ngl.link/api/submit',
                headers={
                    'content-type': 'application/x-www-form-urlencoded',
                    'user-agent': 'Mozilla/5.0',
                    'referer': f'https://ngl.link/{username}'
                },
                data={
                    'username': username,
                    'question': message,
                    'deviceId': '0',
                    'gameSlug': '',
                    'referrer': ''
                },
                proxies=get_proxy(),
                timeout=10,
                verify=False
            )
            if response.status_code == 200:
                sent += 1
        except:
            continue
        time.sleep(random.uniform(0.2, 0.5))
    results[thread_id] = sent

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    username = data['username']
    message = data['message']
    count = int(data['count'])
    threads = []
    thread_count = 50  # Sửa thành 50 thread
    results = {}

    for i in range(thread_count):
        t = threading.Thread(target=send_message,
                             args=(username, message, count // thread_count, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_sent = sum(results.values())
    return jsonify({"success": True, "sent": total_sent})

# Hàm check proxy sống/chết
def check_proxy(proxy):
    try:
        response = requests.get(
            'https://httpbin.org/ip',
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=5
        )
        if response.status_code == 200:
            print(f"[OK] Proxy hoạt động: {proxy}")
        else:
            print(f"[FAIL] Proxy lỗi: {proxy}")
    except:
        print(f"[FAIL] Proxy lỗi: {proxy}")

# Hàm test toàn bộ proxy
def test_all_proxies():
    with open("proxy.txt", "r") as f:
        proxies = [line.strip() for line in f if line.strip()]

    for proxy in proxies:
        check_proxy(proxy)

if __name__ == '__main__':
    # test_all_proxies()  # Bỏ comment dòng này nếu muốn test proxy trước khi chạy app
    app.run(debug=True)
