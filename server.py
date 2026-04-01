from fastapi import FastAPI, Request
from groq import Groq
from dotenv import load_dotenv
import os
import threading
import requests
import time

load_dotenv()

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Datos de WhatsApp
PHONE_NUMBER_ID = "1039371239261216"
WHATSAPP_TOKEN = "EAAetHkCYgWcBRCkicffPXj1zWBDu1RAvtwhVB1SoDx5S1bOhblnfu6ntvbHYSzwDuWaIKiZCHpkVpRwYDy5ZAOeZBJeZBLW9cKM8xfh4pQ7CwkeZAjBTs8TxwTM941jlPs0wFTEZB1fua2cevMtC5fi3ZCZBqC74ZCwifhpBiZBY4ZCrI1lNTUQkuFaaA6h0Q02viK8wFxVKNlQo0FTj9ShLl2lAbCUD9W7s6LAT88InkyINlJIJeZBjy6S5DurGN38ZBMnwfBqCIfnV9spjPAWkxQKeK"

SYSTEM_PROMPT = """
Eres un asistente de ventas amable y profesional para una barbería llamada "BarberPro".
Tu único objetivo es responder preguntas, verificar disponibilidad y agendar citas.
Horario: Lunes a Sábado, 9am a 7pm.
Servicios: Corte $15, Corte + Barba $25, Afeitado $10.
Cuando el cliente quiera una cita, pide: nombre, servicio deseado y hora preferida.
Responde siempre en español, de forma corta y amigable.
NUNCA inventes información que no tienes.
"""

historiales = {}

def enviar_whatsapp(telefono, mensaje):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {"body": mensaje}
    }
    requests.post(url, headers=headers, json=data)

@app.get("/")
def root():
    return {"status": "Setter AI corriendo ✅"}

@app.get("/webhook")
async def verificar_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.verify_token") == "mi_token_secreto":
        return int(params.get("hub.challenge"))
    return {"error": "Token invalido"}

@app.post("/webhook")
async def recibir_whatsapp(request: Request):
    data = await request.json()
    try:
        mensaje = data["entry"][0]["changes"][0]["value"]["messages"][0]
        texto = mensaje["text"]["body"]
        telefono = mensaje["from"]

        if telefono not in historiales:
            historiales[telefono] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

        historiales[telefono].append({"role": "user", "content": texto})

        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=historiales[telefono]
        )

        texto_respuesta = respuesta.choices[0].message.content
        historiales[telefono].append({"role": "assistant", "content": texto_respuesta})

        enviar_whatsapp(telefono, texto_respuesta)

    except:
        pass

    return {"status": "ok"}

@app.post("/mensaje")
async def recibir_mensaje(request: Request):
    data = await request.json()
    usuario_id = data.get("usuario_id", "default")
    mensaje = data.get("mensaje", "")

    if usuario_id not in historiales:
        historiales[usuario_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    historiales[usuario_id].append({"role": "user", "content": mensaje})

    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=historiales[usuario_id]
    )

    texto = respuesta.choices[0].message.content
    historiales[usuario_id].append({"role": "assistant", "content": texto})

    return {"respuesta": texto}

def self_ping():
    time.sleep(60)
    while True:
        time.sleep(25)
        try:
            requests.get("https://setter-ai-tv96.onrender.com/")
            print("✅ Self-ping enviado")
        except:
            print("❌ Error en self-ping")

threading.Thread(target=self_ping, daemon=True).start()