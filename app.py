from flask import Flask, request, jsonify, render_template
import requests
import time
import uuid
import random

app = Flask(__name__, template_folder='templates')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

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

    results = []
    for i in range(count):
        device_id = str(uuid.uuid4())
        user_agent = random.choice(USER_AGENTS)

        headers = {
            "Host": "ngl.link",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://ngl.link",
            "referer": f"https://ngl.link/{username}",
            "user-agent": user_agent
        }

        payload = {
            "username": username,
            "question": message,
            "deviceId": device_id,
            "gameSlug": "",
            "referrer": ""
        }

        try:
            response = requests.post("https://ngl.link/api/submit", headers=headers, data=payload)
            print(f"[RESPONSE {i+1}] {response.status_code}: {response.text}")

            try:
                json_resp = response.json()
                success = json_resp.get("success", False)
                error = json_resp.get("error", "")
            except Exception as e:
                success = False
                error = str(e)

            results.append({
                'status_code': response.status_code,
                'success': success,
                'message': f"Sent {i+1}/{count}" + (f" - {error}" if not success else "")
            })

        except Exception as ex:
            results.append({
                'status_code': 0,
                'success': False,
                'message': f"Sent {i+1}/{count} - exception: {str(ex)}"
            })

        time.sleep(1)  # Delay giữa các lần gửi để tránh bị block

    return jsonify({ "results": results })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
