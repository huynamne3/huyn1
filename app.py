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
    for i in range(count):
        proxy = get_proxy()
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
                proxies=proxy,
                timeout=10,
                verify=False
            )
            if response.status_code == 200:
                sent += 1
                print(f"[Thread {thread_id}] Sent {i+1}/{count} ✅ via {proxy['http']}")
            else:
                print(f"[Thread {thread_id}] Failed {i+1}/{count} ❌ Status: {response.status_code}")
        except Exception as e:
            print(f"[Thread {thread_id}] Lỗi kết nối {i+1}/{count} ❌ Proxy: {proxy['http']} | Error: {e}")
        time.sleep(random.uniform(0.2, 0.5))
    results[thread_id] = sent


@app.route('/send', methods=['POST'])
def send():
    data = request.json
    username = data['username']
    message = data['message']
    count = int(data['count'])
    threads = []
    thread_count = 50
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

if __name__ == '__main__':
    app.run(debug=True)
