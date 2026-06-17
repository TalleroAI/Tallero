from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/health")
def health():
    return {"status": "ok", "message": "Tallero AI funcionando"}
