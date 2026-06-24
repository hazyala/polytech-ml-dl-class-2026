"""Minimal LangChain LCEL chain demo.

Requires packages from lab/requirements.txt, especially langchain-core.
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda


def fake_llm_value(messages):
    last = messages.to_messages()[-1].content
    return f"Local fake response for: {last}"


def main() -> None:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a class demo assistant."),
            ("human", "Explain {topic} in one sentence."),
        ]
    )
    chain = prompt | RunnableLambda(fake_llm_value) | StrOutputParser()
    print(chain.invoke({"topic": "LangChain LCEL"}))


if __name__ == "__main__":
    main()

