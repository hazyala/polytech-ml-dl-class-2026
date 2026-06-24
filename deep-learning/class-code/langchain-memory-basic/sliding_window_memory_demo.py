"""Conversation sliding-window memory starter."""

from collections import deque


class SlidingWindowMemory:
    def __init__(self, max_turns: int = 3) -> None:
        self.max_turns = max_turns
        self.turns: deque[tuple[str, str]] = deque(maxlen=max_turns)

    def add_turn(self, user: str, assistant: str) -> None:
        self.turns.append((user, assistant))

    def build_prompt_context(self) -> str:
        lines = []
        for index, (user, assistant) in enumerate(self.turns, start=1):
            lines.append(f"[turn {index}] user: {user}")
            lines.append(f"[turn {index}] assistant: {assistant}")
        return "\n".join(lines)


def main() -> None:
    memory = SlidingWindowMemory(max_turns=2)
    memory.add_turn("KNN이 뭐야?", "가까운 이웃으로 분류하는 알고리즘입니다.")
    memory.add_turn("k는 무슨 뜻이야?", "참고할 이웃의 개수입니다.")
    memory.add_turn("너무 크면?", "경계가 부드러워지고 세부 패턴을 놓칠 수 있습니다.")
    print(memory.build_prompt_context())


if __name__ == "__main__":
    main()

