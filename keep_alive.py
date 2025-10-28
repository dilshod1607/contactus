import os
import asyncio
from threading import Thread
from flask import Flask, request, jsonify
from flask_cors import CORS  # 🟢 qo‘shildi
from handlers.users.admin import new_request_handler
from loader import dp, db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 🟢 barcha domenlarga ruxsat

main_loop = asyncio.get_event_loop()


@app.route("/", methods=["GET"])
def home():
    return "Contact API ishlayapti ✅"


@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json(force=True)
    fio = data.get("fio")
    phone = data.get("phone")
    email = data.get("email")
    message = data.get("message")

    if not fio or not phone or not email or not message:
        return jsonify({"status": "error", "message": "Barcha maydonlarni to'ldiring"}), 400

    try:
        req_id = db.add_request(fio, phone, email, message)

        asyncio.run_coroutine_threadsafe(
            new_request_handler(fio, phone, email, message, req_id),
            main_loop
        )

        return jsonify({"status": "success", "message": "Xabar botga yuborildi va saqlandi!", "id": req_id}), 200
    except Exception as e:
        app.logger.exception("❌ Handler xato: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500


def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    Thread(target=run_flask, daemon=True).start()
