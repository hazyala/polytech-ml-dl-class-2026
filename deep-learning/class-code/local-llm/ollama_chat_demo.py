"""Minimal Ollama chat example for the Local LLM lecture."""

import argparse
import requests


def chat(prompt: str, model: str, base_url: str) -> str:
    response = requests.post(
        f"{base_url.rstrip('/')}/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", default="머신러닝을 한 문단으로 설명해줘.")
    parser.add_argument("--model", default="llama3.2")
    parser.add_argument("--base-url", default="http://localhost:11434")
    args = parser.parse_args()

    print(chat(args.prompt, args.model, args.base_url))


if __name__ == "__main__":
    main()

