# Kindle2txt

Kindle2txtは、Kindle電子書籍のテキストを自動的に抽出するPythonツールです。スクリーンショットとOCR技術を組み合わせて、Kindleアプリで表示されている電子書籍のテキストをテキストファイルとして保存します。

※ 本READMEは、AIによって自動生成されています。

## 特徴

- Kindleアプリの自動操作によるページめくり
- スクリーンショットの自動取得
- Google Gemini AIを使用した高精度OCR
- テキストレイアウトの保持
- ヘッダー、フッター、ページ番号の自動除外

## 必要条件

- Python 3.8以上
- macOS（OSXのみ対応）
- Kindleデスクトップアプリケーション
- Google Gemini API キー

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/juv-shun/kindle2txt.git
cd kindle2txt

# 必要なパッケージをインストール
poetry install
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
    "output_directory": "./output"
}
```

3. スクリプトを実行します：

```bash
python main.py
```

4. 指示に従ってKindleアプリを準備し、テキスト抽出を開始します：
   - Kindleアプリが自動的に起動します
   - 抽出したい本の最初のページに移動します
   - ターミナルに戻ってEnterキーを押すと、自動抽出が開始されます

5. 抽出されたテキストは`output`ディレクトリに保存されます

## 設定オプション

- `screenshot_region`: スクリーンショットを取得する画面領域 [x, y, width, height]
- `kindle_app_name`: Kindleアプリケーションの名前
- `page_turn_delay`: ページめくり後の待機時間（秒）
- `activation_delay`: Kindleアプリ起動後の待機時間（秒）
- `page_turn_direction`: ページめくりの方向（"right" または "left"）
- `output_directory`: 抽出されたテキストの保存先ディレクトリ

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
