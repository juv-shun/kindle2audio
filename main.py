import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pyautogui
from google import genai
from google.genai import types
from PIL import Image


def load_config():
    """OSに応じて適切な設定ファイルをロードする"""
    config_path = Path(__file__).with_name("config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"設定ファイル config.json が見つかりません。")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# グローバル変数として `config` をロード
config = load_config()
shutdown_flag = False
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]


def image_hash(image):
    """画像データの MD5 ハッシュを生成し、一意の識別子を返す"""
    try:
        return hashlib.md5(image.tobytes()).hexdigest()
    except (MemoryError, ValueError) as e:
        print(f"画像ハッシュの生成中にエラーが発生しました: {e}")
        return None


def activate_kindle_app(kindle_app_name):
    """Kindle アプリをアクティブ化する"""
    try:
        subprocess.run(["osascript", "-e", f'tell application "{kindle_app_name}" to activate'], check=True)
        time.sleep(2)
    except subprocess.SubprocessError:
        print("エラー: Kindle アプリをアクティブ化できませんでした。")
        sys.exit(1)


def minimize_kindle_app(kindle_app_name):
    """Kindle アプリを最小化する"""
    try:
        # 改良版AppleScript：ウィンドウが存在するか確認してから最小化
        applescript_command = f"""
        tell application "{kindle_app_name}"
            if it is running then
                try
                    if (count of windows) > 0 then
                        set miniaturized of window 1 to true
                    end if
                on error
                    -- ウィンドウ操作に失敗した場合は静かに終了
                end try
            end if
        end tell
        """
        subprocess.run(["osascript", "-e", applescript_command], check=False)
        print(f"{kindle_app_name}の最小化処理を完了しました。")
    except Exception as e:
        print(f"Info: {kindle_app_name} の最小化中に例外が発生しましたが、処理は継続します: {e}")


def monitor_exit():
    # エンターを2回打ち込むとプログラムを終了するための監視
    global shutdown_flag
    print("途中で作業を終了するには、エンターを2回押してください。")
    count = 0
    while not shutdown_flag:
        line = input()
        if line == "":
            count += 1
            if count >= 2:
                print("終了要求が受け付けられました。処理を停止します。")
                shutdown_flag = True
                break
        else:
            count = 0


def setup_screenshot():
    """スクリーンショット開始位置の設定を促すメッセージを表示し、エンターキー入力後にKindleを最大化"""
    message = "スクリーンショット開始位置にページ位置を設定したら、ターミナル画面に戻ってEnterキーを押してください。"
    try:
        subprocess.run(["osascript", "-e", f'display notification "{message}" with title "Kindle2Image"'])
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
        subprocess.run(["osascript", "-e", applescript_command])
    except subprocess.SubprocessError:
        print("エラー: Kindle のフルスクリーン化に失敗しました。")


def capture_screenshot():
    """指定された領域のスクリーンショットを取得"""
    try:
        screenshot = pyautogui.screenshot(region=config["screenshot_region"])
        return screenshot
    except Exception as e:
        print(f"スクリーンショット取得中にエラー: {e}")
        return None


def ensure_output_directory():
    """出力ディレクトリが存在することを確認し、なければ作成する"""
    if not os.path.exists(config["output_directory"]):
        os.makedirs(config["output_directory"])
        print(f"出力ディレクトリを作成しました: {config['output_directory']}")


def capture_screenshots():
    # Kindleのスクリーンショットを連続取得し、ファイルに保存する
    print("📸 スクリーンショットの取得を開始します...")
    last_image_hash = None
    page = 1

    # 出力ディレクトリの確認
    ensure_output_directory()

    while True:
        if shutdown_flag:
            print("終了要求によりスクリーンショットの取得を停止します。")
            break

        screenshot = capture_screenshot()
        if screenshot is None:
            time.sleep(0.1)
            continue

        current_image_hash = image_hash(screenshot)
        if last_image_hash == current_image_hash:
            print("🔄 ページの変化がないため終了")
            break

        # OCRを実行
        ocr_text = ocr(screenshot)

        # OCR結果をファイルに保存
        file_path = os.path.join(config["output_directory"], f"page_{page:03d}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ocr_text)
        print(f"📄 ページ {page} のOCR結果を保存しました: {file_path}")

        last_image_hash = current_image_hash

        # Kindleのページを送る
        pyautogui.press(config["page_turn_direction"])
        time.sleep(config["page_turn_delay"])
        page += 1


def ocr(image: Image.Image) -> str:
    """GeminiでOCRを実行"""
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = (
        "この画像からすべてのテキストを抽出してください。レイアウトをできるだけ保持し、段落や改行を維持してください。"
        "各ページには、ヘッダーとフッターが含まれている場合があります。その場合、ヘッダーとフッターを除いてテキストを抽出してください。"
        "また、ページの終わりには、ページ番号が表示されていることがあります。その場合、それを除いてテキストを抽出してください。"
    )

    response = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt, image])
    return response.text


def play_completion_sound():
    """処理完了時に通知音を再生する"""
    try:
        os.system("afplay /System/Library/Sounds/Glass.aiff")
    except Exception as e:
        print(f"通知音の再生中に例外が発生しましたが、処理は継続します: {e}")


def main():
    # Kindleアプリをアクティブ化
    activate_kindle_app(config["kindle_app_name"])

    # スクリーンショット開始位置の設定
    setup_screenshot()

    time.sleep(config["activation_delay"])

    # 終了監視スレッドを開始
    monitor_thread = threading.Thread(target=monitor_exit, daemon=True)
    monitor_thread.start()

    # スクリーンショットを取得開始
    capture_screenshots()

    print("✅ スクリーンショット取得完了")

    # 処理完了後に音を鳴らす
    play_completion_sound()

    # Kindleを最小化する
    minimize_kindle_app(config["kindle_app_name"])

    print(f"スクリーンショットは {config['output_directory']} ディレクトリに保存されました。")


if __name__ == "__main__":
    main()
