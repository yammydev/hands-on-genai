#!/usr/bin/env python3
"""Simple CLI quiz game powered by Ollama (gemma4:e2b)."""

from __future__ import annotations

import json
import string
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass

OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma4:e2b"


@dataclass
class Quiz:
    question: str
    choices: list[str]
    answer_index: int  # 0-3
    explanation: str


def request_quiz_from_ollama() -> Quiz:
    """Generate one common-sense 4-choice quiz via Ollama and parse it."""
    prompt = (
        "あなたはクイズ作成AIです。\n"
        "常識クイズを1問だけ作ってください。\n"
        "以下のJSONだけを出力してください（他の文字は不要）。\n"
        "{\n"
        '  "question": "問題文",\n'
        '  "choices": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],\n'
        '  "answer_index": 1,\n'
        '  "explanation": "正解の簡単な解説"\n'
        "}\n"
        "answer_indexは0〜3の整数で指定してください。"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {
                "role": "system",
                "content": "ユーザ指定のJSONスキーマに厳密に従って出力してください。",
            },
            {"role": "user", "content": prompt},
        ],
    }

    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Ollamaに接続できませんでした。Ollamaが起動しているか確認してください。"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("OllamaレスポンスのJSON解析に失敗しました。") from exc

    try:
        raw_content = response_data["message"]["content"]
        quiz_data = json.loads(raw_content)
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("クイズ生成結果の形式が不正です。") from exc

    validate_quiz_data(quiz_data)

    return Quiz(
        question=quiz_data["question"],
        choices=quiz_data["choices"],
        answer_index=quiz_data["answer_index"],
        explanation=quiz_data["explanation"],
    )


def validate_quiz_data(data: dict) -> None:
    required_keys = {"question", "choices", "answer_index", "explanation"}
    if not isinstance(data, dict) or not required_keys.issubset(data.keys()):
        raise RuntimeError("クイズに必要な項目が不足しています。")

    if not isinstance(data["question"], str) or not data["question"].strip():
        raise RuntimeError("問題文が不正です。")

    if not isinstance(data["choices"], list) or len(data["choices"]) != 4:
        raise RuntimeError("選択肢は4つ必要です。")

    if any(not isinstance(choice, str) or not choice.strip() for choice in data["choices"]):
        raise RuntimeError("選択肢の形式が不正です。")

    if not isinstance(data["answer_index"], int) or not 0 <= data["answer_index"] <= 3:
        raise RuntimeError("answer_indexは0〜3の整数である必要があります。")

    if not isinstance(data["explanation"], str):
        raise RuntimeError("解説の形式が不正です。")


def get_user_answer() -> int:
    """Accept A-D or 1-4 and return index 0-3."""
    pass


def run_quiz() -> None:
    print("=== 常識クイズゲーム ===")
    print("クイズを生成中です...\n")

    quiz = request_quiz_from_ollama()

    print(f"問題: {quiz.question}")
    for i, choice in enumerate(quiz.choices):
        label = string.ascii_uppercase[i]
        print(f"  {label}. {choice}")

    user_answer_index = get_user_answer()
    correct = user_answer_index == quiz.answer_index

    print("\n=== 結果 ===")
    if correct:
        print("正解です！")
    else:
        correct_label = string.ascii_uppercase[quiz.answer_index]
        print(f"不正解です。正解は {correct_label} です。")

    if quiz.explanation.strip():
        print(f"解説: {quiz.explanation}")


def main() -> int:
    pass


if __name__ == "__main__":
    raise SystemExit(main())
