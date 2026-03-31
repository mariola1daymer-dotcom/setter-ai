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

@app.get("/")
def root():
    return {"status": "Setter AI corriendo ✅"}

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