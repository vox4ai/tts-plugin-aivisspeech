# tts-plugin-aivisspeech

[AivisSpeech Engine](https://github.com/AivisProject/AivisSpeech-Engine) 用の TTS プラグインです。

## 🛠 概要
- **役割**: AivisSpeech Engine の REST API を介して、`tts-plugin-bridge` から音声合成を行う。
- **主要機能**:
    - VOICEVOX 互換 API への接続。
    - スタイル ID 指定による話者制御。
    - WAV 形式での音声出力。

## ⚙️ 前提条件
- **AivisSpeech Engine** が起動しており、REST API サーバー（デフォルト: `http://localhost:10101`）が有効であること。

## 🚀 開発・実行
- **パッケージ管理**: `uv`
- **テスト**: `pytest`

## 🔗 関連リポジトリ
- `repos/tts-plugin-bridge`: コアフレームワーク
