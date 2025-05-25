from flask import Flask, request, jsonify
import requests
import random
import time
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app)  # Cho phép gọi từ domain ngoài

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

# Danh sách user-agent để giả lập trình duyệt/người dùng khác nhau
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A107F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)",
    # Có thể thêm nhiều để tránh bị phát hiện
]

def send_message(username, message):
    url = "https://ngl.link/api/submit"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://ngl.link",
        "Referer": f"https://ngl.link/{username}",
    }

    payload = {
        "username": username,
        "question": message,
        "deviceId": f"device_{random.randint(100000,999999)}"
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception:
        return False

@app.route("/send-attack", methods=["POST"])
def send_attack():
    data = request.get_json()
    username = data.get("username")
    message = data.get("message", "")
    count = int(data.get("count", 1))

    if not username:
        return jsonify({"success": False, "error": "Thiếu username"}), 400

    results = []
    for i in range(count):
        msg = message if message else f"Tin nhắn #{i+1} 🤖"
        success = send_message(username, msg)
        results.append({
            "attempt": i + 1,
            "status": "✅ Thành công" if success else "❌ Thất bại",
            "message": msg
        })
        time.sleep(0.5)  # Delay để tránh bị chặn

    return jsonify({"success": True, "results": results})

if __name__ == "__main__":
    app.run(debug=True)
