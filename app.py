from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests, uuid, time, random
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/90 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0) AppleWebKit/605.1.15 Mobile/15A5341f Safari/604.1"
]

EMOJIS = ["😂", "🤣", "😎", "💀", "🔥", "🤡", "👻", "😈", "👽", "🫠", "🥶", "😱"]
MESSAGES = [
    "Đã 6677 rồi còn dùng nglink trẻ trâu hả em",
    "Còn dùng ngl là còn FA",
    "Rep đi chứ để làm gì :))",
    "Ngầu vậy mà cần ẩn danh à?"
]

def get_random_message():
    msg = random.choice(MESSAGES)
    emojis = ' '.join(random.choices(EMOJIS, k=random.randint(1, 3)))
    return f"{msg} {emojis}"

def send_single(username, message, proxy, index):
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
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }

    try:
        res = requests.post("https://ngl.link/api/submit", headers=headers, data=payload, proxies=proxies, timeout=10)
        return {
            'success': res.status_code == 200,
            'message': f"Đã gửi {index + 1}",
            'code': res.status_code
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Lỗi gửi {index + 1}",
            'error': str(e)
        }

@app.route('/send-attack', methods=['POST'])
def send_attack():
    data = request.json
    username = data.get('username')
    user_message = data.get('message')
    total = int(data.get('count', 1))

    if not username or total <= 0:
        return jsonify({'error': 'Thiếu username hoặc số lượng không hợp lệ'}), 400

    # Load proxies
    with open('live_proxies.txt', 'r') as f:
        proxy_list = [line.strip() for line in f if line.strip()]

    jobs = []
    index = 0

    for proxy in proxy_list:
        for _ in range(50):  # 3 thread per proxy
            if index >= total:
                break
            msg = user_message or get_random_message()
            jobs.append((username, msg, proxy, index))
            index += 1
        if index >= total:
            break

    results = []
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        futures = [executor.submit(send_single, *job) for job in jobs]
        for f in futures:
            results.append(f.result())

    return jsonify({
        'results': results,
        'time_taken': f"{round(time.time() - start_time, 2)}s"
    })

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
