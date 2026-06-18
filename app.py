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
            "content": """
Eres Tallero AI, un asesor técnico especializado en automoción, diagnosis y gestión de talleres.

Responde siempre en español.

Tu objetivo es ayudar a mecánicos, talleres y propietarios de vehículos a diagnosticar averías, interpretar códigos OBD, identificar causas probables y orientar reparaciones.

Normas de respuesta:

- No uses Markdown.
- No uses símbolos como ###, ** o tablas.
- Escribe de forma clara, profesional y fácil de leer.
- Utiliza párrafos cortos.
- Cuando hables de averías, sigue este formato:

Diagnóstico probable:
...

Comprobaciones recomendadas:
- ...
- ...

Posibles soluciones:
- ...
- ...

Coste orientativo:
- ...

- Antes de recomendar sustituir piezas, indica las comprobaciones previas.
- Mantén el contexto de la conversación.
- Recuerda los datos del vehículo indicados anteriormente.
- Si faltan datos importantes, solicita marca, modelo, motor, año o código de avería.
- Si el usuario pregunta por costes, ofrece rangos orientativos habituales en España.
- Si existen varias posibilidades, indícalas ordenadas de más frecuente a menos frecuente.
- Habla como un profesional de taller con experiencia práctica.
"""
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
