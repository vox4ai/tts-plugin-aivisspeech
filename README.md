# tts-plugin-aivisspeech

<p align="center">
  <img src="https://via.placeholder.com/1200x400/1a1a1a/ffffff?text=tts-plugin-aivisspeech" alt="tts-plugin-aivisspeech Banner" width="1200">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/pypi-latest-blue.svg" alt="PyPI version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-yellow.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/maintained%3F-yes-brightgreen.svg" alt="Maintained">
</p>

<p align="center">
  <a href="https://github.com/vox4ai/tts-plugin-aivisspeech">Website</a> •
  <a href="https://github.com/vox4ai/tts-plugin-aivisspeech/issues">Report Bug</a> •
  <a href="https://github.com/vox4ai/tts-plugin-aivisspeech/contributing">Contributing</a>
</p>

---

## 🚀 Overview

[AivisSpeech Engine](https://github.com/AivisProject/AivisSpeech-Engine) 用 TTS プラグイン。`tts-plugin-bridge` のプラグインとして動作します。

## 📦 インストール

```bash
# bridge プロジェクトにプラグインとして追加
cd repos/tts-plugin-bridge
uv add ../tts-plugin-aivisspeech
```

## 🛠 Usage

### 🎤 Bridge CLI 経由

```bash
# 話者一覧を確認（Engine が起動している必要あり）
curl -s http://localhost:10101/speakers | python3 -m json.tool

# 音声合成して WAV ファイルに保存
uv run python -m tts_plugin_bridge.skill synthesize "こんにちは" \
    --engine aivisspeech \
    --server-url http://localhost:10101 \
    --style-id 888753760 \
    --output hello.wav

# 直接再生（Linux の場合 paplay / aplay が必要）
uv run python -m tts_plugin_bridge.skill synthesize "こんにちは" \
    --engine aivisspeech \
    --server-url http://localhost:10101 \
    --style-id 888753760 \
    --play

# 接続テスト
uv run python -m tts_plugin_bridge.skill test \
    --engine aivisspeech \
    --server-url http://localhost:10101 \
    --style-id 888753760
```

### 🧩 Python API 経由

```python
from tts_plugin_aivisspeech.connector import AivisSpeechConnector
from tts_plugin_bridge.protocol import TTSRequest

async with AivisSpeechConnector(server_url="http://localhost:10101") as c:
    req = TTSRequest(text="こんにちは", speed=1.0, extra={"style_id": 888753760})
    resp = await c.synthesize(req)
    with open("output.wav", "wb") as f:
        f.write(resp.audio_data)
```

## 📊 スタイル ID

AivisSpeech Engine の話者スタイル ID は動的（32bit 符号付き整数）です。
`/speakers` エンドポイントで現在の Engine が持つ話者とスタイル ID を確認できます。

例:
| 話者 | スタイル | ID |
|------|----------|----|
| まお | ノーマル | 888753760 |
| まお | ふつー | 888753761 |
| まお | あまあま | 888753762 |
| コハク | ノーマル | 1878365376 |

## 🔍 検証環境

- **OS**: Windows 11 + WSL2 (Ubuntu)
- **AivisSpeech Engine**: v1.2.0 (まお / コハク)
- **確認日**: 2026-05-09
- **確認内容**: Bridge CLI からの synthesize / test / --play 全て動作確認済み
  - 実際の Engine に対して音声合成 → WAV 出力 (44100Hz, 16bit, mono PCM)
  - paplay による直接再生も確認

## 📜 ライセンス

MIT License