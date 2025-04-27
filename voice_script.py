import json
import os
from pathlib import Path

from google import genai
from google.genai import types

genai_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def main():
    # configファイルをロード
    config = load_config()

    # 原稿を読み込む
    manuscript_path = Path(__file__).with_name(config["output_directory"]) / config["output_filename"]
    with open(manuscript_path, "r", encoding="utf-8") as f:
        manuscript = f.read()

    # 章の数を取得
    chapter_count = get_chapters(manuscript)

    # ユーザに読み聞かせスクリプトを作成する章を尋ねる
    user_prompt = specify_chapter(chapter_count)

    # システムプロンプトを読み込む
    with open(Path(__file__).with_name("prompts") / "voice_script_system.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # Geminiで読み聞かせスクリプトを作成
    script = generate_voice_script(system_prompt, user_prompt, manuscript)

    # 読み聞かせスクリプトを保存
    save_voice_script(script)


def load_config():
    """OSに応じて適切な設定ファイルをロードする"""
    config_path = Path(__file__).with_name("config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError("設定ファイル config.json が見つかりません。")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_chapters(manuscript: str) -> int:
    """
    原稿の章が何章構成かを返す

    Args:
        manuscript (str): 原稿

    Returns:
        int: 章の数
    """
    prompt = "原稿の章が何章構成かを教えてください。回答は、半角数字で返してください。"
    response = genai_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, manuscript],
    )
    return int(response.text)


def specify_chapter(chapter_count: int) -> str:
    """
    ユーザに読み聞かせスクリプトを作成する章を尋ねる

    Args:
        chapter_count (int): 章の数

    Returns:
        str: 読み聞かせスクリプトを作成する章
    """
    chapters = [f"第{i}章" for i in range(1, chapter_count + 1)]
    print("読み聞かせスクリプトを作成したい章を選択してください:")
    for idx, chap in enumerate(chapters, start=1):
        print(f"{idx}. {chap}")
    while True:
        choice = input(f"番号で選択してください (1-{chapter_count}): ")
        if choice in [str(i) for i in range(1, chapter_count + 1)]:
            chapter = chapters[int(choice) - 1]
            break
        print("無効な選択です。1〜3の番号を入力してください。")
    return chapter


def generate_voice_script(system_prompt: str, user_prompt: str, manuscript: str):
    """
    テキストを読み聞かせ用スクリプトを作成

    Args:
        system_prompt (str): システムプロンプト
        user_prompt (str): ユーザープロンプト
        manuscript (str): 原稿
    """

    print(f"🚀 {user_prompt}の読み聞かせスクリプトの生成を開始します...")
    response = genai_client.models.generate_content(
        model="gemini-2.5-pro-preview-03-25",
        contents=[user_prompt, types.Part(text=manuscript)],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )
    return response.text


def save_voice_script(script: str):
    # スクリプトを出力ファイルに保存
    output_path = Path(__file__).with_name("output") / "voice_script.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(script)

    print(f"読み聞かせスクリプトを {output_path} に保存しました。")


if __name__ == "__main__":
    main()
