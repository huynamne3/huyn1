from flask import Flask, request, jsonify, render_template
import requests
import time

app = Flask(__name__, template_folder='templates')

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
        headers = {
            "Host": "ngl.link",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://ngl.link",
            "referer": f"https://ngl.link/{username}"
        }

        payload = {
            "username": username,
            "question": message,
            "deviceId": "0",
            "gameSlug": "",
            "referrer": ""
        }

        response = requests.post("https://ngl.link/api/submit", headers=headers, data=payload)
        results.append({
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'message': f"Sent {i+1}/{count}"
        })
        time.sleep(0.5)

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
