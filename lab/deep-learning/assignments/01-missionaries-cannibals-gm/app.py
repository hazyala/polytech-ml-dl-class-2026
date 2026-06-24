# =============================================
# app.py
# 식인종-선교사 LLM GM 웹앱 Flask 서버
# 강의자료(Chapter 2) Flask 기반 구현
# =============================================

from flask import Flask, render_template, request, jsonify, session
import os, json

from game_engine import (
    Status,
    game,
    judge,
    get_valid_commands,
    get_safe_commands,
    find_solution_command,
    COMMAND_NAMES,
)
from llm_gm import gm_select_command, gm_comment

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dl1_secret_key")


def status_from_dict(d):
    """딕셔너리 → Status 객체 변환"""
    return Status(d["left_m"], d["left_c"], d["right_m"], d["right_c"], d["boat"])


@app.route("/")
def index():
    """메인 게임 화면"""
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def start():
    """게임 시작 - 초기 상태 반환"""
    status = Status()
    session["status"]  = status.to_dict()
    session["history"] = []
    session["visited"] = [status.to_tuple()]
    session["turn"]    = 0

    valid = get_valid_commands(status)
    return jsonify({
        "status":         status.to_dict(),
        "valid_commands": valid,
        "command_names":  COMMAND_NAMES,
        "turn":           0,
    })


@app.route("/api/ai_turn", methods=["POST"])
def ai_turn():
    """
    AI(LLM GM)가 커맨드를 선택하고 한 턴 진행
    PPT 자동화 흐름: 환경 → Command(자동화) → 다음 환경 → 판정
    """
    if "status" not in session:
        return jsonify({"error": "게임을 먼저 시작하세요."}), 400

    status  = status_from_dict(session["status"])
    history = session.get("history", [])
    visited = [tuple(v) for v in session.get("visited", [])]
    turn    = session.get("turn", 0)

    valid = get_valid_commands(status)
    if not valid:
        return jsonify({"result": "gameover", "message": "실행 가능한 커맨드가 없습니다."})

    # AI 문제해결: BFS로 승리 경로의 다음 수를 찾고, LLM은 GM 해설을 담당한다.
    safe_commands = get_safe_commands(status, visited)
    cmd_id = find_solution_command(status, visited)
    if cmd_id is None:
        cmd_id = gm_select_command(status, safe_commands or valid)
    cmd_name = COMMAND_NAMES[cmd_id]

    # 게임 엔진 실행
    next_status = game(status, cmd_id)
    if next_status is None:
        return jsonify({"result": "invalid", "message": f"커맨드 {cmd_name} 실행 불가"})

    # PPT 문제 상황 2: 이미 방문한 상태 체크
    if next_status.to_tuple() in visited:
        # 다른 커맨드 재시도
        for alt in valid:
            if alt == cmd_id:
                continue
            alt_status = game(status, alt)
            if alt_status and alt_status.to_tuple() not in visited:
                cmd_id      = alt
                cmd_name    = COMMAND_NAMES[alt]
                next_status = alt_status
                break

    result = judge(next_status)

    # GM 해설 생성
    comment = gm_comment(next_status, cmd_name, result)

    # 히스토리 기록
    history.append({
        "turn":       turn + 1,
        "command":    cmd_id,
        "cmd_name":   cmd_name,
        "status":     next_status.to_dict(),
        "result":     result,
        "comment":    comment,
    })

    visited.append(list(next_status.to_tuple()))
    session["status"]  = next_status.to_dict()
    session["history"] = history
    session["visited"] = visited
    session["turn"]    = turn + 1

    return jsonify({
        "turn":           turn + 1,
        "command":        cmd_id,
        "cmd_name":       cmd_name,
        "status":         next_status.to_dict(),
        "result":         result,
        "comment":        comment,
        "valid_commands": get_valid_commands(next_status) if result == "continue" else [],
    })


@app.route("/api/manual_turn", methods=["POST"])
def manual_turn():
    """
    사용자가 직접 커맨드를 선택하는 수동 모드
    """
    if "status" not in session:
        return jsonify({"error": "게임을 먼저 시작하세요."}), 400

    data    = request.get_json()
    cmd_id  = int(data.get("command", 0))
    status  = status_from_dict(session["status"])
    history = session.get("history", [])
    visited = [tuple(v) for v in session.get("visited", [])]
    turn    = session.get("turn", 0)

    valid = get_valid_commands(status)
    if cmd_id not in valid:
        return jsonify({"error": "실행 불가능한 커맨드입니다."}), 400

    next_status = game(status, cmd_id)
    if next_status is None:
        return jsonify({"error": "커맨드 실행 실패"}), 400

    result   = judge(next_status)
    cmd_name = COMMAND_NAMES[cmd_id]
    comment  = gm_comment(next_status, cmd_name, result)

    history.append({
        "turn":     turn + 1,
        "command":  cmd_id,
        "cmd_name": cmd_name,
        "status":   next_status.to_dict(),
        "result":   result,
        "comment":  comment,
    })

    visited.append(list(next_status.to_tuple()))
    session["status"]  = next_status.to_dict()
    session["history"] = history
    session["visited"] = visited
    session["turn"]    = turn + 1

    return jsonify({
        "turn":           turn + 1,
        "command":        cmd_id,
        "cmd_name":       cmd_name,
        "status":         next_status.to_dict(),
        "result":         result,
        "comment":        comment,
        "valid_commands": get_valid_commands(next_status) if result == "continue" else [],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5101))
    app.run(host="0.0.0.0", port=port, debug=True)
