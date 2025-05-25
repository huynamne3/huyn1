from flask import Flask, request, jsonify
import threading
import random
import requests
import time

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')
proxies = []

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
                verify=False  # bỏ SSL check để tránh lỗi proxy
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
    thread_count = 5
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
