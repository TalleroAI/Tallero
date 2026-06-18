from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])

    openai_messages = [
        {
            "role": "system",
            "content": """Eres Tallero AI, un asistente técnico para talleres y profesionales de automoción.

Responde siempre en español.

Tu función es ayudar con:
- diagnóstico de averías
- códigos OBD
- mantenimiento
- recambios
- síntomas de vehículos
- orientación técnica

Mantén el contexto de la conversación.
Si el usuario pregunta "cuánto costaría", usa los síntomas o vehículo mencionados antes.
No inventes referencias exactas de recambios si faltan datos.
Si falta información importante, pide marca, modelo, motor, año o código de avería."""
        }
    ]

    openai_messages.extend(messages)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=openai_messages
    )

    return jsonify({
        "reply": response.choices[0].message.content
    })

@app.route("/health")
def health():
    return {"status": "ok", "message": "Tallero AI funcionando"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
