from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from twilio.rest import Client
import os
import logging

app = Flask(__name__, static_folder='dist')
CORS(app)
logging.basicConfig(level=logging.INFO)

# Environment Variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.environ.get("MY_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    logging.info(f"Received: {data}")
    try:
        message_body = f"לקוח חדש!\nשם: {data['name']}\nאימייל: {data['email']}\nטלפון: {data['phone']}\nכמות משלוחים: {data['shipments']}"
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=MY_WHATSAPP_NUMBER,
            body=message_body
        )
        return jsonify({"status": "success", "sid": message.sid}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

# Serve React build
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
