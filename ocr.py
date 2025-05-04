import hashlib
import json
import os
import subprocess
import threading
import time
from pathlib import Path

import pyautogui
from google import genai
from PIL import Image

SHUTDOWN_FLAG = False
genai_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def main():
    # configファイルをロード
    config = load_config()

    # Kindleアプリをアクティブ化
    subprocess.run(["osascript", "-e", f'tell application "{config["kindle_app_name"]}" to activate'], check=True)
    time.sleep(2)

    # スクリーンショット開始準備
    setup_screenshot()
    time.sleep(config["activation_delay"])

    # 終了監視スレッドを開始
    monitor_thread = threading.Thread(target=monitor_exit, daemon=True)
    monitor_thread.start()

    # 出力ディレクトリの準備
    if not os.path.exists(config["output_directory"]):
        os.makedirs(config["output_directory"])
        print(f"出力ディレクトリを作成しました: {config['output_directory']}")

    # スクリーンショットを取得開始
    print("📸 スクリーンショットの取得を開始します...")
    capture_screenshots(config)
    print("✅ スクリーンショット取得完了")

    # 処理完了後に音を鳴らす
    os.system("afplay /System/Library/Sounds/Glass.aiff")

    print(f"スクリーンショットは {config['output_directory']} ディレクトリに保存されました。")


def load_config():
    """OSに応じて適切な設定ファイルをロードする"""
    config_path = Path(__file__).with_name("config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError("設定ファイル config.json が見つかりません。")

    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def setup_screenshot():
    """スクリーンショット開始位置の設定を促すメッセージを表示し、エンターキー入力後にKindleを最大化"""
    message = "スクリーンショット開始位置にページ位置を設定したら、ターミナル画面に戻ってEnterキーを押してください。"
    try:
        subprocess.run(["osascript", "-e", f'display notification "{message}" with title "Kindle2Image"'], check=False)
    except subprocess.SubprocessError:
        print("エラー: 通知の送信に失敗しました。")

    print("\n=== Kindle2Image ===")
    print(f"📌 {message}")
    input("準備ができたらEnterキーを押してください...")

    # Kindleをフルスクリーン化
    try:
        applescript_command = """
        tell application "System Events"
            tell process "Amazon Kindle"
                set frontmost to true
                keystroke "f" using {command down, control down}
            end tell
        end tell
        """
        subprocess.run(["osascript", "-e", applescript_command], check=False)
    except subprocess.SubprocessError:
        print("エラー: Kindle のフルスクリーン化に失敗しました。")


def monitor_exit():
    """エンターを2回打ち込むとプログラムを終了するための監視"""
    global SHUTDOWN_FLAG
    print("途中で作業を終了するには、エンターを2回押してください。")
    count = 0
    while not SHUTDOWN_FLAG:
        line = input()
        if line == "":
            count += 1
            if count >= 2:
                print("終了要求が受け付けられました。処理を停止します。")
                SHUTDOWN_FLAG = True
                break
        else:
            count = 0


def capture_screenshots(config):
    """Kindleのスクリーンショットを連続取得し、ファイルに保存する"""
    last_image_hash = None
    page = 1

    while True:
        if SHUTDOWN_FLAG:
            print("終了要求によりスクリーンショットの取得を停止します。")
            break

        screenshot = pyautogui.screenshot(region=config["screenshot_region"])

        current_image_hash = hashlib.md5(screenshot.tobytes()).hexdigest()
        if last_image_hash == current_image_hash:
            print("🔄 ページの変化がないため終了")
            break

        # OCRを実行
        ocr_text = ocr(screenshot)

        # OCR結果を単一ファイルに追記
        file_path = Path(__file__).with_name(config["output_directory"]) / config["output_filename"]
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(ocr_text)
            f.write("\n")
        print(f"📄 ページ {page} のOCR結果を追記しました: {file_path}")

        last_image_hash = current_image_hash

        # Kindleのページを送る
        pyautogui.press(config["page_turn_direction"])
        time.sleep(config["page_turn_delay"])
        page += 1


with open(Path(__file__).with_name("prompts") / "ocr.txt", encoding="utf-8") as f:
    prompt = f.read()


def ocr(image: Image.Image) -> str:
    """GeminiでOCRを実行"""
    response = genai_client.models.generate_content(model="gemini-2.0-flash", contents=[prompt, image])
    return response.text


if __name__ == "__main__":
    main()
