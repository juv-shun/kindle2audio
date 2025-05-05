# kindle2audio

kindle2audioは、Kindle電子書籍のテキストを自動的に抽出するPythonツールです。スクリーンショットとOCR技術を組み合わせて、Kindleアプリで表示されている電子書籍のテキストをテキストファイルとして保存します。また、読み聞かせ用スクリプトを生成し、VoiceVoxによる高品質音声合成も可能です。

※ 本READMEは、AIによって自動生成されています。

## 特徴

- Kindleアプリの自動操作によるページめくり
- スクリーンショットの自動取得
- Google Gemini AIを使用した高精度OCR
- テキストレイアウトの保持
- ヘッダー、フッター、ページ番号の自動除外
- Gemini AIによる読み聞かせ用スクリプト生成
- VoiceVoxによる高品質音声合成

## 必要条件

- Python 3.8以上
- macOS（OSXのみ対応）
- Kindleデスクトップアプリケーション
- Google Gemini API キー
- VoiceVoxエンジン（ローカル実行またはクラウドサービス）

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/juv-shun/kindle2audio.git
cd kindle2audio

# 必要なパッケージをインストール
uv pip sync
```

## 使い方

1. 環境変数に`GEMINI_API_KEY`を設定します：

```bash
export GEMINI_API_KEY="あなたのGemini APIキー"
```

2. `config.json`ファイルを必要に応じて編集します：

```json
{
    "screenshot_region": [70, 70, 1850, 1000],
    "kindle_app_name": "Amazon Kindle",
    "page_turn_delay": 1,
    "activation_delay": 5,
    "page_turn_direction": "right",
    "image_format": "png",
    "output_directory": "output"
}
```

3. スクリプトを実行します：

```bash
python ocr.py
```

4. 指示に従ってKindleアプリを準備し、テキスト抽出を開始します：
   - Kindleアプリが自動的に起動します
   - 抽出したい本の最初のページに移動します
   - ターミナルに戻ってEnterキーを押すと、自動抽出が開始されます

5. 抽出されたテキストは`output`ディレクトリに保存されます

6. 読み聞かせ用スクリプトを生成します：
```bash
python script.py
```
   - 生成された`script.txt`は`output`ディレクトリに保存されます  
   - 実行時に対象の章を番号で選択してください

7. VoiceVoxエンジンを起動し、音声ファイルを合成します：
```bash
python synthesis.py
```
   - 実行前にVoiceVoxエンジンが起動している必要があります（例：`docker run -p 50021:50021 voicevox/voicevox_engine:cpu`）  
   - 合成された`audio.wav`が`output`ディレクトリに保存されます

## プログラム概要

kindle2audioは主に以下の3つのPythonスクリプトで構成されています：

### ocr.py

Kindleアプリから自動的にスクリーンショットを取得し、テキストを抽出するための主要なスクリプトです。

- Kindleアプリの自動起動とフルスクリーン化
- ページめくりの自動化（右または左キーを使用）
- スクリーンショットの自動取得と一時保存
- Google Gemini AIを利用した高精度OCR処理
- テキストファイルへの変換結果の保存
- 同一ページの検出による自動終了機能

### script.py

抽出されたテキストから、Gemini AIを使用して読み聞かせ用のスクリプトを生成します。

- 抽出されたテキストから章構成の自動判別
- ユーザーによる対象章の選択インターフェース
- Gemini AIによる読み聞かせに適した台本の生成
- 生成されたスクリプトのテキストファイルへの保存

### synthesis.py

読み聞かせスクリプトをVoiceVoxエンジンを使用して音声に変換します。

- スクリプトの行ごとに音声合成APIを呼び出し
- 一時的な音声ファイルの生成と管理
- 複数の音声ファイルの一つのWAVファイルへの結合
- 最終的な音声ファイルの出力ディレクトリへの保存

## 設定オプション

- `screenshot_region`: スクリーンショットを取得する画面領域 [x, y, width, height]
- `kindle_app_name`: Kindleアプリケーションの名前
- `page_turn_delay`: ページめくり後の待機時間（秒）
- `activation_delay`: Kindleアプリ起動後の待機時間（秒）
- `page_turn_direction`: ページめくりの方向（"right" または "left"）
- `output_directory`: 抽出されたテキストの保存先ディレクトリ
- `output_filename`: 抽出されたテキストの保存ファイル名

## 操作方法

- 実行中にEnterキーを2回押すと、処理を途中で終了できます
- 同じページが2回連続で検出された場合（本の最後に達した場合）、処理は自動的に終了します

## 注意事項

- このツールは個人的な使用目的のみを想定しています
- 著作権法を遵守し、抽出したテキストの取り扱いには十分注意してください
- スクリーンショット領域は、お使いのディスプレイ解像度に合わせて調整が必要な場合があります

## ライセンス

MITライセンス

## 作者

[juv-shun](https://github.com/juv-shun)
