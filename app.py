from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    pregunta = data.get("message", "")

    respuesta = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """Eres Tallero AI, un experto en automoción.
Ayudas a talleres mecánicos con:
- diagnóstico de averías
- códigos OBD
- mantenimiento
- recambios
- información técnica"""
            },
            {
                "role": "user",
                "content": pregunta
            }
        ]
    )

    return jsonify({
        "reply": respuesta.choices[0].message.content
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
