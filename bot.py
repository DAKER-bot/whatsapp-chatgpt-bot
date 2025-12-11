from flask import Flask, request, jsonify
import requests
from openai import OpenAI
import os

app = Flask(__name__)

# Variables d'environnement
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Route GET pour la vérification du webhook Meta
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# Route POST pour recevoir les messages WhatsApp
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        number = message["from"]
        user_text = message["text"]["body"]

        # Réponse naturelle (comme un humain)
        reply = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es une vraie personne, chaleureuse et simple. "
                        "Réponds naturellement, comme un ami. "
                        "Ne dis jamais que tu es une IA ou un robot. "
                        "Sois humain, sympa, court et naturel."
                    )
                },
                {"role": "user", "content": user_text}
            ]
        )

        bot_reply = reply.choices[0].message["content"]

        # Envoyer la réponse sur WhatsApp
        send_message(number, bot_reply)

    except Exception as e:
        print("Erreur :", e)

    return "ok", 200

def send_message(number, message):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": number,
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

@app.route("/", methods=["GET"])
def home():
    return "Bot WhatsApp en ligne !"

