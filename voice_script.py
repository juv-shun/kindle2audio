import json
import os
from pathlib import Path

from google import genai
from google.genai import types

genai_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def main():
    # configファイルをロード
    config = load_config()

    # ユーザに第何章を読み聞かせスクリプトにするかを尋ねる
    user_prompt = input("第何章を読み聞かせスクリプトにするかを入力してください: ")

    # 原稿ファイルのパスを取得
    manuscript_path = Path(__file__).with_name(config["output_directory"]) / config["output_filename"]

    # システムプロンプトを読み込む
    with open(Path(__file__).with_name("prompts") / "voice_script_system.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # Geminiで読み聞かせスクリプトを作成
    generate_voice_script(system_prompt, user_prompt, manuscript_path)


def load_config():
    """OSに応じて適切な設定ファイルをロードする"""
    config_path = Path(__file__).with_name("config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError("設定ファイル config.json が見つかりません。")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_voice_script(system_prompt: str, user_prompt: str, manuscript_path: Path):
    """
    テキストを読み聞かせ用スクリプトを作成

    Args:
        system_prompt (str): システムプロンプト
        user_prompt (str): ユーザープロンプト
        manuscript_path (Path): 原稿ファイルのパス
    """
    with open(manuscript_path, "r", encoding="utf-8") as f:
        manuscript_content = f.read()
    manuscript = types.Part(text=manuscript_content)

    response = genai_client.models.generate_content(
        model="gemini-2.5-pro-preview-03-25",
        contents=[user_prompt, manuscript],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )

    # スクリプトを出力ファイルに保存
    output_path = Path(__file__).with_name("output") / "voice_script.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"読み聞かせスクリプトを {output_path} に保存しました。")


if __name__ == "__main__":
    main()
