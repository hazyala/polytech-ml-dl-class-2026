"""Minimal Flask API server for the Python API lecture."""

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify({"message": "Flask API is running"})


@app.get("/api/echo")
def echo_get():
    return jsonify({"text": request.args.get("text", "")})


@app.post("/api/echo")
def echo_post():
    payload = request.get_json(silent=True) or {}
    return jsonify({"text": payload.get("text", ""), "payload": payload})


@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    values = payload.get("values", [])
    if not isinstance(values, list) or not all(isinstance(v, (int, float)) for v in values):
        return jsonify({"error": "values must be a list of numbers"}), 400
    return jsonify({"prediction": sum(values) / len(values) if values else 0})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

