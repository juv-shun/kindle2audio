import tempfile
import wave
from pathlib import Path

import requests

# APIのベースURL
VOICEVOX_BASE_URL = "http://localhost:50021"
# VOICEVOX_BASE_URL = "https://voicevoxengine-production.up.railway.app"
SPEAKER_ID = 8
headers = {"Content-Type": "application/json"}


def main():
    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)

        file_count = 1
        for line in open(Path(__file__).with_name("output") / "script.txt", "r", encoding="utf-8"):
            # 空行はスキップ
            line = line.strip()
            if not line:
                continue

            # /audio_query APIを呼び出してクエリを作成
            response = requests.post(
                f"{VOICEVOX_BASE_URL}/audio_query", headers=headers, params={"text": line, "speaker": SPEAKER_ID}
            )

            # /synthesis APIを呼び出して音声合成
            response = requests.post(
                f"{VOICEVOX_BASE_URL}/synthesis",
                headers=headers,
                params={"speaker": SPEAKER_ID},
                json=response.json(),
            )

            with open(temp_dir / f"voice_{file_count:03d}.wav", "wb") as wf:
                wf.write(response.content)

            print(f"音声合成が完了しました。voice_{file_count:03d}.wavを保存しました。")
            file_count += 1

            # temp_wavディレクトリの内容をoutput/audio.wavに結合
            join_wav(sorted(temp_dir.glob("*.wav")), Path(__file__).with_name("output") / "audio.wav")
            print("音声合成が完了しました。output/audio.wavを保存しました。")


def join_wav(inputs: list[Path], output: Path):
    fps = [wave.open(str(file), "rb") for file in inputs]
    fpw = wave.open(str(output), "w")
    fpw.setnchannels(fps[0].getnchannels())
    fpw.setsampwidth(fps[0].getsampwidth())
    fpw.setframerate(fps[0].getframerate())
    for fp in fps:
        fpw.writeframes(fp.readframes(fp.getnframes()))
        fp.close()
    fpw.close()


if __name__ == "__main__":
    main()
