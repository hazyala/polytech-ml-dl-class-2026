# =============================================
# llm_gm.py
# LLM이 GM 역할 - 현재 상태를 보고 커맨드 자동 선택
# 강의자료(Chapter 4) Role-based Prompting 방식 활용
# =============================================

import os
import sys

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "common"))

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from game_engine import COMMAND_NAMES

# Ollama 연결 설정
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL    = os.environ.get("OLLAMA_MODEL", "gemma4:e2b")

# ── 시스템 프롬프트 (게임 규칙 주입) ──────────────────────────
SYSTEM_PROMPT = """당신은 식인종-선교사 강 건너기 게임의 GM입니다.

[게임 규칙]
- 왼쪽 강가의 선교사 3명, 식인종 3명을 배로 모두 오른쪽으로 옮기면 승리
- 배는 한 번에 최대 2명 탑승, 배가 있는 쪽 인원만 태울 수 있음
- 어느 쪽이든 선교사가 1명 이상인데 식인종보다 적으면 게임오버

[커맨드 번호]
0: 선교사 1명
1: 선교사 2명
2: 식인종 1명
3: 식인종 2명
4: 선교사 1명 + 식인종 1명

반드시 실행 가능한 커맨드 번호 중 하나만 숫자로 답하세요. 다른 말은 하지 마세요."""

# LangChain LCEL 체인 구성 (강의자료 Chapter 5 방식)
_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{situation}"),
])
_llm   = ChatOllama(model=OLLAMA_MODEL, temperature=0.1, base_url=OLLAMA_BASE_URL)
_chain = _prompt | _llm | StrOutputParser()


def gm_select_command(status, valid_commands):
    """
    현재 상태와 실행 가능한 커맨드 목록을 LLM에 전달하여
    GM이 최선의 커맨드 번호를 선택하도록 함
    """
    # 현재 상황을 텍스트로 구성
    valid_desc = ", ".join([f"{i}({COMMAND_NAMES[i]})" for i in valid_commands])
    situation = (
        f"현재 상태:\n"
        f"  왼쪽 - 선교사 {status.left_m}명, 식인종 {status.left_c}명\n"
        f"  오른쪽 - 선교사 {status.right_m}명, 식인종 {status.right_c}명\n"
        f"  배 위치: {status.boat}\n\n"
        f"실행 가능한 커맨드: {valid_desc}\n\n"
        f"어떤 커맨드를 실행할까요? 번호만 답하세요."
    )

    try:
        result = _chain.invoke({"situation": situation})
        # 응답에서 숫자만 추출
        for ch in result.strip():
            if ch.isdigit() and int(ch) in valid_commands:
                return int(ch)
    except Exception:
        pass

    # LLM 응답 실패 시 첫 번째 유효 커맨드 반환
    return valid_commands[0]


def gm_comment(status, command_name, result):
    """
    GM이 각 턴마다 상황 해설을 짧게 생성
    """
    comment_prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 식인종-선교사 게임 해설자입니다. 한 문장으로 짧게 상황을 설명하세요."),
        ("human", "{situation}"),
    ])
    comment_chain = comment_prompt | _llm | StrOutputParser()

    situation = (
        f"커맨드 '{command_name}' 실행 결과: {result}\n"
        f"현재 오른쪽에 선교사 {status.right_m}명, 식인종 {status.right_c}명이 있습니다."
    )
    try:
        return comment_chain.invoke({"situation": situation})
    except Exception:
        return f"{command_name} 실행 완료."
