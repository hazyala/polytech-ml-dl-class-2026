"""Minimal ComfyUI queue-prompt client.

Run ComfyUI first, then pass a workflow JSON file exported from ComfyUI.
"""

import argparse
import json
from pathlib import Path

import requests


def queue_prompt(workflow_path: Path, base_url: str) -> dict:
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    response = requests.post(
        f"{base_url.rstrip('/')}/prompt",
        json={"prompt": workflow},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--base-url", default="http://localhost:8188")
    args = parser.parse_args()
    print(queue_prompt(args.workflow, args.base_url))


if __name__ == "__main__":
    main()

