"""
공통 Ollama(LangChain) 클라이언트 모듈
강의 자료(Chapter 4, 5, 6) 기반으로 작성
- ChatOllama 인스턴스 생성
- ConversationChain(멀티턴) 빌더
- LCEL 체인 빌더
"""
import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Ollama 서버 주소 (환경 변수 또는 기본값)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL    = os.environ.get("OLLAMA_MODEL", "gemma3:4b")


def get_llm(temperature: float = 0.7) -> ChatOllama:
    """ChatOllama 인스턴스 반환"""
    return ChatOllama(
        model=OLLAMA_MODEL,
        temperature=temperature,
        base_url=OLLAMA_BASE_URL,
    )


def build_conversation_chain(temperature: float = 0.7) -> ConversationChain:
    """
    멀티턴 대화용 ConversationChain 생성
    강의 자료(Chapter 6) ConversationBufferMemory 방식 활용
    """
    llm    = get_llm(temperature)
    memory = ConversationBufferMemory()
    chain  = ConversationChain(llm=llm, memory=memory, verbose=False)
    return chain


def build_lcel_chain(system_prompt: str, temperature: float = 0.2):
    """
    LCEL 파이프라인 체인 생성 (강의 자료 Chapter 5 방식)
    prompt | llm | StrOutputParser
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human",  "{input}"),
    ])
    llm   = get_llm(temperature)
    chain = prompt | llm | StrOutputParser()
    return chain
