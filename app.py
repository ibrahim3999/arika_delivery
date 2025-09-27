from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os

app = Flask(__name__, static_folder='dist')
CORS(app)

# Twilio credentials
TWILIO_ACCOUNT_SID = "AC422776bc7c1d025cccf035a6757a6f03"
TWILIO_AUTH_TOKEN = "620760aa0f49f3b50e525b95fe8eb078"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
MY_WHATSAPP_NUMBER = "whatsapp:+972502334565"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    shipments = data.get("shipments")

    message_body = f"לקוח חדש!\nשם: {name}\nאימייל: {email}\nטלפון: {phone}\nכמות משלוחים: {shipments}"

    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=MY_WHATSAPP_NUMBER,
            body=message_body
        )
        return jsonify({"status": "success", "sid": message.sid}), 200
    except TwilioRestException as e:
        return jsonify({"status": "error", "error": e.msg, "code": e.code}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# Serve React build
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
