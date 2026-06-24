"""Small conversation-memory demo without requiring a paid LLM API."""

from collections import deque


class WindowMemory:
    def __init__(self, size: int = 4) -> None:
        self.messages: deque[tuple[str, str]] = deque(maxlen=size)

    def add(self, role: str, content: str) -> None:
        self.messages.append((role, content))

    def render(self) -> str:
        return "\n".join(f"{role}: {content}" for role, content in self.messages)


def rule_based_reply(memory: WindowMemory, user_message: str) -> str:
    memory.add("user", user_message)
    reply = (
        "지금까지의 대화 맥락은 아래와 같아요.\n"
        f"{memory.render()}\n"
        "마지막 질문에 답하려면 이 맥락을 프롬프트에 함께 넣으면 됩니다."
    )
    memory.add("assistant", reply)
    return reply


def main() -> None:
    memory = WindowMemory(size=4)
    for message in ["내 이름은 홍길동이야.", "내가 방금 말한 이름이 뭐야?"]:
        print(f"> {message}")
        print(rule_based_reply(memory, message))
        print()


if __name__ == "__main__":
    main()

