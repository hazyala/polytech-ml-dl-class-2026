"""Prompting-pattern examples for Local LLM lectures.

This file builds prompts only. Send the prompt strings to Ollama, ChatGPT, or any
other chat model when you want to compare responses.
"""


def role_prompt(task: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": "You are a concise Korean AI class tutor."},
        {"role": "user", "content": task},
    ]


def few_shot_prompt(topic: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": "Answer with one concept and one simple example."},
        {"role": "user", "content": "Explain KNN."},
        {"role": "assistant", "content": "Concept: classify by nearby samples. Example: vote among 5 nearest Iris flowers."},
        {"role": "user", "content": f"Explain {topic}."},
    ]


def structured_prompt(question: str) -> str:
    return f"""Answer the question using this exact format.

Question: {question}

Format:
1. Key idea:
2. Why it matters:
3. One Python use case:
"""


def main() -> None:
    examples = [
        role_prompt("머신러닝과 딥러닝 차이를 설명해줘."),
        few_shot_prompt("SVM"),
        structured_prompt("What is prompt engineering?"),
    ]
    for item in examples:
        print(item)
        print("-" * 60)


if __name__ == "__main__":
    main()

