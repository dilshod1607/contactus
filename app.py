from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Faqat sizning domeningizga ruxsat beramiz (xavfsizlik uchun)
CORS(app, resources={r"/send": {"origins": "https://bmsm-17.vercel.app"}})

BOT_TOKEN = "8354949877:AAE49hf4h3COf9AAzbFPgAKAxF9pZIAHlZc"      # 🔹 Bu yerga bot tokeningizni yozasiz
CHAT_ID = "5391341271"         # 🔹 Bu yerga adminning chat_id sini yozasiz

@app.route('/send', methods=['POST'])
def send_message():
    try:
        data = request.get_json()

        fio = data.get("fio")
        phone = data.get("phone")
        email = data.get("email")
        message = data.get("message")

        text = f"""
📝 Yangi murojaat keldi:
👤 F.I.O: {fio}
📞 Telefon: {phone}
📧 Email: {email}
💬 Xabar: {message}
"""

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text}

        r = requests.post(url, json=payload)

        if r.status_code == 200:
            return jsonify({"status": "success", "message": "Xabar yuborildi!"})
        else:
            return jsonify({"status": "error", "message": "Telegram API xato"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
