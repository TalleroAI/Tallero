from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from supabase import create_client
import os

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
@app.route("/")
def home():
    return send_from_directory(".", "index.html")
def buscar_conocimiento_tallero(texto):
    try:
        palabras = texto.lower().split()
        filtros = [p for p in palabras if len(p) >= 3]

        if not filtros:
            return ""

        resultados = []

        for palabra in filtros[:6]:
            respuesta = (
                supabase
                .table("knowledge_items")
                .select("titulo,resumen,motor,tags,json_completo")
                .or_(f"titulo.ilike.%{palabra}%,resumen.ilike.%{palabra}%,motor.ilike.%{palabra}%,tags.ilike.%{palabra}%")
                .limit(3)
                .execute()
            )

            if respuesta.data:
                resultados.extend(respuesta.data)

        vistos = set()
        documentos = []

        for item in resultados:
            titulo = item.get("titulo", "")
            if titulo in vistos:
                continue

            vistos.add(titulo)

            documentos.append(f"""
Título: {item.get("titulo", "")}
Motor: {item.get("motor", "")}
Tags: {item.get("tags", "")}
Resumen: {item.get("resumen", "")}
JSON técnico: {item.get("json_completo", "")}
""")

            if len(documentos) >= 3:
                break

        return "\n\n".join(documentos)

    except Exception as e:
        print("Error buscando conocimiento en Supabase:", e)
        return ""
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    ultima_pregunta = messages[-1]["content"] if messages else ""
    conocimiento = buscar_conocimiento_tallero(ultima_pregunta)
openai_messages = [
        {
            "role": "system",
            "content": f"""
Eres Tallero AI, un asesor técnico especializado en automoción, diagnosis y gestión de talleres.

Responde siempre en español.

Tu objetivo es ayudar a mecánicos, talleres y propietarios de vehículos a diagnosticar averías, interpretar códigos OBD, identificar causas probables y orientar reparaciones.

Normas de respuesta:

- No uses Markdown.
- No uses símbolos como ###, ** o tablas.
- Escribe de forma clara, profesional y fácil de leer.
- Utiliza párrafos cortos.
- Cuando hables de averías, sigue este formato:

Utiliza este formato cuando dispongas de información suficiente para realizar un diagnóstico.
Diagnóstico probable:
Explicación breve.

Comprobaciones recomendadas:
- Comprobación 1
- Comprobación 2
- Comprobación 3

Posibles soluciones:
Solo cuando las comprobaciones permitan acotar la avería.

Coste orientativo:
Solo incluir esta sección si el usuario solicita precios o si el diagnóstico está bastante definido.

- Antes de recomendar sustituir piezas, indica las comprobaciones previas.
- Mantén el contexto de la conversación.
- Recuerda los datos del vehículo indicados anteriormente.
- Si faltan datos importantes, solicita marca, modelo, motor, año o código de avería.
- Si el usuario pregunta por costes, ofrece rangos orientativos habituales en España.
- No proporciones costes orientativos salvo que el usuario los pida expresamente.
- Si faltan datos importantes, primero solicita la información necesaria.
- Si faltan datos como motor, año, combustible o kilómetros, no incluyas costes ni soluciones definitivas.
- Cuando falten datos importantes, prioriza hacer preguntas antes de proponer soluciones o costes.
- Evita respuestas largas en la primera consulta.
- Si existen varias posibilidades, indícalas ordenadas de más frecuente a menos frecuente.
- Prioriza siempre las averías más habituales y conocidas del modelo, motor y sistema afectado antes de proponer causas genéricas.
- Ten en cuenta los fallos recurrentes de cada fabricante y motorización cuando la información del vehículo sea suficiente.
- Ordena las posibles causas de más frecuente a menos frecuente según la experiencia habitual en talleres.
- Evita proponer sustituciones costosas sin haber descartado previamente las averías más comunes.
- Habla como un profesional de taller con experiencia práctica.
- Nunca vuelvas a solicitar información que el usuario ya haya proporcionado anteriormente.
- Utiliza toda la información disponible en el historial antes de realizar nuevas preguntas.
- Si ya conoces marca, modelo, motor, combustible, kilometraje o código de avería, no vuelvas a pedirlos.
- Si el usuario ya ha respondido a una pregunta, no vuelvas a formularla de otra manera.
- Si un dato ya ha sido descartado (por ejemplo ausencia de códigos de avería), continúa el diagnóstico sin insistir en ello.
- Prioriza profundizar en las comprobaciones antes que repetir preguntas ya respondidas.
- Evita realizar la misma pregunta varias veces durante la conversación.
- Cuando dispongas de información suficiente para orientar la avería, avanza en el diagnóstico en lugar de solicitar más datos.
- Antes de responder, revisa el contexto completo de la conversación.
- Si el usuario aporta un dato nuevo, intégralo con los datos anteriores.
- Si el usuario cambia de vehículo, empieza un nuevo diagnóstico para ese vehículo.
- Si el usuario indica claramente una marca, modelo o motor diferente, considera cerrado el diagnóstico anterior.
- El vehículo mencionado más recientemente por el usuario tiene prioridad sobre cualquier vehículo indicado anteriormente.
- No reutilices averías, hipótesis o comprobaciones del vehículo anterior salvo que el usuario las relacione explícitamente.
Si existe conocimiento interno relacionado con la consulta, úsalo como prioridad.

Conocimiento interno:

{conocimiento}
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
