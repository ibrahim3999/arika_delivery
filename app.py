from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
import logging

# יצירת אפליקציה
app = Flask(__name__, static_folder='dist')
CORS(app)

# Logging setup
logging.basicConfig(level=logging.INFO)

# קריאה של משתנים מהסביבה
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.environ.get("MY_WHATSAPP_NUMBER")

# בדיקה בסיסית אם כל המשתנים קיימים
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, MY_WHATSAPP_NUMBER]):
    logging.error("Twilio environment variables are missing!")
    raise ValueError("Missing Twilio environment variables!")

# יצירת client של Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    logging.info(f"Received contact data: {data}")

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
        logging.info(f"Message sent successfully, SID: {message.sid}")
        return jsonify({"status": "success", "sid": message.sid}), 200
    except TwilioRestException as e:
        logging.error(f"Twilio error: {e.msg} (code {e.code})")
        return jsonify({"status": "error", "error": e.msg, "code": e.code}), 500
    except Exception as e:
        logging.error(f"General error: {str(e)}")
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
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
