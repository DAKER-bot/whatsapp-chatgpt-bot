from flask import Flask, request, jsonify
import requests
import openai

# ====== CONFIGURATION ======
WHATSAPP_TOKEN = "TON_TOKEN_WHATSAPP"
WHATSAPP_ID = "TON_WHATSAPP_ID"
OPENAI_API_KEY = "TA_CLE_OPENAI"

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

def envoyer_message(numero, texte):
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texte}
    }
    requests.post(url, headers=headers, json=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        numero = message["from"]
        texte = message["text"]["body"]

        # Appel ChatGPT
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": texte}]
        )

        reponse = completion.choices[0].message["content"]

        envoyer_message(numero, reponse)

    except Exception as e:
        print("Erreur webhook:", e)

    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return "Bot WhatsApp bien déployé !"
