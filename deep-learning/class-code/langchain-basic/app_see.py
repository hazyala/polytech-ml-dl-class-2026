from flask import Flask, render_template, request, Response
import time

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("appsse.html")

@app.route("/summarize/stream", methods=["POST"])
def summarize_stream():
    data = request.get_json()
    text = data.get("text", "")

    def generate():
        yield "요약 시작...\n"
        time.sleep(0.5)
        yield f"입력 글자 수: {len(text)}\n"
        time.sleep(0.5)
        yield "요약 결과: 오픈AI가 아마존 AWS와 대규모 클라우드 계약을 체결했다는 내용입니다.\n"

    return Response(generate(), mimetype="text/plain; charset=utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)