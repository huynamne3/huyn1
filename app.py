from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cloudscraper
import time
import uuid

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-attack', methods=['POST'])
def send_attack():
    data = request.json
    print("[REQUEST]", data)
    username = data.get('username')
    message = data.get('message') or "Hello from bot!"
    count = int(data.get('count', 1))

    scraper = cloudscraper.create_scraper()
    results = []
    for i in range(count):
        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://ngl.link",
            "referer": f"https://ngl.link/{username}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        payload = {
            "username": username,
            "question": message,
            "deviceId": str(uuid.uuid4()),
            "gameSlug": "",
            "referrer": ""
        }

        response = scraper.post("https://ngl.link/api/submit", headers=headers, data=payload)

        print(f"[{i+1}] Status Code: {response.status_code}")
        print(f"[{i+1}] Response Text: {response.text}")

        results.append({
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'message': f"Đã gửi {i+1}/{count}",
            'response': response.text
        })

        time.sleep(1.5)  # tăng delay để tránh bị block

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
